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
    logger.info("Запуск синхронизации для лески")

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
    d1 = (today - datetime.timedelta(days=10000)).strftime("%Y-%m-%d")

    client.ensure_headers(sheet, headers)
    skus = client.read_column(sheet, "sku")
    logger.info(f"Найдено артикулов: {len(skus)}")
    logger.info(f"Пример последних SKU: {skus[-5:]}")

    # Очистим старые строки
    client.clear_rows(sheet_name=sheet, start_row=2, num_rows=1500)
    logger.info("Очищены предыдущие строки (до 1500 строк)")

    rows = []
    for sku in skus:
        sku = str(sku).strip()
        if not sku:
            continue
        try:
            info = retry(get_api_info, sku=sku, d1=d1, d2=d2)
            if all(v == '' for k, v in info.items() if k != "sku"):
                logger.warning(f"API пустой, пробуем парсинг HTML для SKU {sku}")
                info = retry(get_html_info, sku=sku)

            logger.info(f"Данные по SKU {sku}: {info}")
            row = [info.get(col, "") for col in headers]

            if any(cell for cell in row[1:]):  # если есть хоть одно значение кроме sku
                rows.append(row)
            else:
                logger.warning(f"Пустой результат по SKU {sku}")
        except Exception as e:
            logger.error(f"Ошибка при обработке SKU {sku}: {e}")

    if rows:
        client.write_rows(sheet, start_row=2, rows=rows)
        logger.info(f"Записано строк: {len(rows)}")
    else:
        logger.warning("Нет данных для записи")

    logger.info("Синхронизация завершена.")

if __name__ == "__main__":
    main()
