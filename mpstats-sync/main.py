import logging
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import datetime
from sheets_client import SheetsClient
from mpstats_client import get_product_info as get_api_info
from parser import get_product_info as get_html_info
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

    today = datetime.date.today()
    d2 = today.strftime("%Y-%m-%d")
    d1 = (today - datetime.timedelta(days=30)).strftime("%Y-%m-%d")

    client.ensure_headers(sheet, headers)
    skus = client.read_column(sheet, "sku")
    logger.info(f"Found {len(skus)} SKUs")

    rows = []
    for sku in skus:
        try:
            # Пытаемся через API
            info = retry(get_api_info, sku=sku, d1=d1, d2=d2)
            if all(v == '' for k, v in info.items() if k != "sku"):
                logger.warning(f"API пустой, пробуем парсинг для SKU {sku}")
                info = retry(get_html_info, sku=sku)

            logger.info(f"Parsed info for SKU {sku}: {info}")
            rows.append([info.get(col, "") for col in headers])
        except Exception as e:
            logger.error(f"Failed to fetch info for SKU {sku}: {e}")

    if rows:
        client.write_rows(sheet, start_row=2, rows=rows)

    logger.info("Sync complete.")

if __name__ == "__main__":
    main()
