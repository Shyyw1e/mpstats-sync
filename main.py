import logging
from dotenv import load_dotenv
load_dotenv()

import datetime
from parser import get_product_info as parse_fallback
from sheets_client import SheetsClient
from mpstats_client import get_product_info
from utils import retry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting sync process")

    client = SheetsClient()
    sheet = "Леска"
    headers = [
        "sku", "Наименование", "Длина", "Толщина лески",
        "Вид лески", "Материал лески",
        "Максимальная нагрузка", "Вид рыбы",
        "Спортивное назначение", "Цвет"
    ]

    # d2 = сегодня, d1 = 30 дней назад
    today = datetime.date.today()
    d2 = today.strftime("%Y-%m-%d")
    d1 = (today - datetime.timedelta(days=30)).strftime("%Y-%m-%d")

    # 1) Установить заголовки
    client.ensure_headers(sheet, headers)

    # 2) Прочитать все SKU из столбца "sku"
    skus = client.read_column(sheet, "sku")
    logger.info(f"Found {len(skus)} SKUs")

    # 3) Для каждого SKU получить данные и собрать строки
    rows = []
    for sku in skus:
        try:
            info = retry(get_product_info, sku=sku, d1=d1, d2=d2)
            if all(v == '' for v in info.values()):
                logger.warning(f"API пустой, пробуем fallback для SKU {sku}")
                info = retry(parse_fallback, sku=sku)
            logger.info(f"Parsed info for SKU {sku}: {info}")
            rows.append([info.get(col, "") for col in headers])
        except Exception as e:
            logger.error(f"Failed to fetch info for SKU {sku}: {e}")

    # 4) Записать всё, начиная со второй строки
    if rows:
        client.write_rows(sheet, start_row=2, rows=rows)

    logger.info("Sync complete.")

if __name__ == "__main__":
    main()
