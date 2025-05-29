import os
import logging
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

API_TOKEN = os.getenv('MPSTATS_API_TOKEN')
BASE_URL = 'https://mpstats.io/api/wb/get'

def get_product_info(sku: str) -> dict:
    try:
        # Получаем последнюю версию
        version_url = f"{BASE_URL}/item/{sku}/full_page/versions?d1=2024-01-01&d2=2025-12-31"
        headers = {'X-Mpstats-TOKEN': API_TOKEN}
        resp = requests.get(version_url, headers=headers)
        resp.raise_for_status()
        versions = resp.json()
        version = versions[-1]['version'] if versions else ""

        # Загружаем страницу товара
        page_url = f"https://mpstats.io/item/{sku}/full_page?version={version}"
        page = requests.get(page_url)
        soup = BeautifulSoup(page.text, 'html.parser')

        attrs = {}
        for row in soup.select('.product-attribute'):
            name = row.select_one('.attr-name')
            value = row.select_one('.attr-value')
            if name and value:
                attrs[name.get_text(strip=True)] = value.get_text(strip=True)

        # Преобразуем атрибуты в поля таблицы
        mapping = {
            "Длина (м)": "Длина",
            "Толщина лески": "Толщина лески",
            "Вид лески": "Вид лески",
            "Материал лески": "Материал лески",
            "Максимальная нагрузка": "Максимальная нагрузка",
            "Вид рыбы": "Вид рыбы",
            "Спортивное назначение": "Спортивное назначение",
            "Цвет": "Цвет",
        }

        result = {"sku": sku}

        for source_key, target_key in mapping.items():
            for attr_key in attrs:
                if attr_key.lower().startswith(source_key.lower()):
                    result[target_key] = attrs[attr_key]
                    break
            else:
                result[target_key] = ""

        # Получаем наименование
        name_block = soup.select_one(".product-name")
        result["Наименование"] = name_block.text.strip() if name_block else ""

        return result

    except Exception as e:
        logger.error(f"HTML parse failed for SKU {sku}: {e}")
        return {"sku": sku}

