# main_reels.py

import logging
import datetime
from dotenv import load_dotenv
load_dotenv()

from sheets_client import SheetsClient
from mpstats_reels import get_reel_info
from utils import retry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Запуск синхронизации для катушек")

    client = SheetsClient()
    sheet = "Катушка"

    headers = [
        "sku",
        "Вид катушки",
        "Емкость катушки",
        "Количество подшипников (шт.)",
        "Передаточное отношение",
        "Размер шпули"
    ]

    today = datetime.date.today()
    d2 = today.strftime("%Y-%m-%d")
    d1 = (today - datetime.timedelta(days=30)).strftime("%Y-%m-%d")

    client.ensure_headers(sheet, headers)
    skus = client.read_column(sheet, "sku")
    logger.info(f"Найдено артикулов: {len(skus)}")
    logger.info(f"Пример последних SKU: {skus[-5:]}")

    rows = []
    for sku in skus:
        sku = str(sku).strip()
        if not sku:
            continue
        try:
            info = retry(get_reel_info, sku=sku, d1=d1, d2=d2)
            logger.info(f"Данные по SKU {sku}: {info}")
            row = [info.get(col, "") for col in headers]

            if any(cell for cell in row[1:]):  # если не только sku
                rows.append(row)
            else:
                logger.warning(f"Пустой результат по SKU {sku}")
        except Exception as e:
            logger.error(f"Ошибка при обработке SKU {sku}: {e}")

    if rows:
        client.write_rows(sheet, start_row=2, rows=rows)
        logger.info(f"Записано строк: {len(rows)}")
    else:
        logger.warning("Нет данных для записи.")

    logger.info("Синхронизация завершена.")

if __name__ == "__main__":
    main()
