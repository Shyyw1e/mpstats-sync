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
    url = f"{BASE_URL}/item/{sku}/full_page/versions?d1=2025-01-01&d2=2025-12-31"
    headers = {'X-Mpstats-TOKEN': API_TOKEN}
    logger.debug(f"MPstats API request: {url}")
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    # Берём последнюю версию
    version = data[-1]
    # Теперь парсим страницу, чтобы вытащить атрибуты
    page = requests.get(f"https://mpstats.io/item/{sku}/full_page")
    soup = BeautifulSoup(page.text, 'html.parser')
    attrs = {}
    # Примерные селекторы — поправьте под вашу страницу
    for row in soup.select('.product-attribute'):
        name = row.select_one('.attr-name').get_text(strip=True)
        val = row.select_one('.attr-value').get_text(strip=True)
        attrs[name] = val
    return {
        'name': attrs.get('Наименование'),
        'length': attrs.get('Длина'),
        'thickness': attrs.get('Толщина лески'),
        'type': attrs.get('Вид лески'),
        'material': attrs.get('Материал лески'),
        'max_load': attrs.get('Максимальная нагрузка'),
        'fish_type': attrs.get('Вид рыбы'),
        'sport': attrs.get('Спортивное назначение'),
        'color': attrs.get('Цвет'),
    }
