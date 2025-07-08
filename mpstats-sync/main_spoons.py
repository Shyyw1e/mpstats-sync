import logging
import datetime
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from sheets_client import SheetsClient
from mpstats_spoons import get_spoon_info
from utils import retry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Запуск синхронизации для Блесны")

    client = SheetsClient()
    sheet = "Блесны"

    headers = [
        "sku", "Наименование", "Вес товара без упаковки (г)", "Материал изделия",
        "Количество предметов в упаковке", "Тип блесны", "Модель блесны",
        "Вид крючка", "Длина приманки (мм)", "Вид рыбы", "Спортивное назначение",
        "Цвет", "Комплектация"
    ]

    today = datetime.date.today()
    d2 = today.strftime("%Y-%m-%d")
    d1 = (today - datetime.timedelta(days=10000)).strftime("%Y-%m-%d")

    client.ensure_headers(sheet, headers)
    skus = client.read_column(sheet, "sku")
    logger.info(f"Найдено артикулов: {len(skus)}")

    rows = []
    for sku in skus:
        sku = str(sku).strip()
        if not sku:
            continue
        try:
            info = retry(get_spoon_info, sku=sku, d1=d1, d2=d2)
            logger.info(f"Данные по SKU {sku}: {info}")
            row = [info.get(col, "") for col in headers]

            if any(cell for cell in row[1:]):
                rows.append(row)
            else:
                logger.warning(f"Пустой результат для {sku}")
        except Exception as e:
            logger.exception(f"Ошибка при обработке SKU {sku}: {e}")

    client.clear_rows(sheet, start_row=2, num_rows=10000)
    
    if rows:
        client.write_rows(sheet, start_row=2, rows=rows)
        logger.info(f"Записано строк: {len(rows)}")
    else:
        logger.warning("Нет данных для записи.")

    logger.info("Синхронизация завершена.")

if __name__ == "__main__":
    main()