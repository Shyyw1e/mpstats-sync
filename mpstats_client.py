# mpstats_client.py

import os
import logging
import requests
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

API_TOKEN = os.getenv("MPSTATS_API_TOKEN")
BASE_URL = "https://mpstats.io/api/wb/get"

# Сопоставление названий из API с колонками таблицы
FIELD_MAPPING = {
    "Толщина лески": "Толщина лески",
    "Толщина (мм)": "Толщина лески",
    "Длина (м)": "Длина",
    "Вид лески": "Вид лески",
    "Материал лески": "Материал лески",
    "Максимальная нагрузка": "Максимальная нагрузка",
    "Цвет": "Цвет"
    # Остальные поля парсятся через парсер или оставляются пустыми
}

def get_versions(sku: str, d1: str, d2: str) -> list:
    url = f"{BASE_URL}/item/{sku}/full_page/versions"
    params = {"d1": d1, "d2": d2}
    headers = {"X-Mpstats-TOKEN": API_TOKEN} if API_TOKEN else {}
    logger.debug(f"Request to MPSTATS versions: {url} params={params}")
    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()
    return resp.json()

def get_product_info(sku: str, d1: str, d2: str) -> dict:
    versions = get_versions(sku, d1, d2)
    logger.info(f"Versions for {sku}: {versions}")
    latest = versions[0].get("version") if versions else ""

    url = f"{BASE_URL}/item/{sku}/full_page"
    params = {"version": latest}
    headers = {"X-Mpstats-TOKEN": API_TOKEN} if API_TOKEN else {}
    logger.debug(f"Request to MPSTATS product: {url} params={params}")
    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    logger.info(f"Full page data for {sku}: {data}")

    # Парсим параметры
    param_names = data.get("param_names", [])
    param_values = data.get("param_values", [])
    raw_attrs = dict(zip(param_names, param_values))

    info = {"sku": sku}

    for source_key, target_col in FIELD_MAPPING.items():
        for param_name in raw_attrs:
            if param_name.lower().startswith(source_key.lower()):
                info[target_col] = raw_attrs[param_name]
                break
        else:
            info[target_col] = ""

    # Прямые поля
    info["Наименование"] = data.get("full_name", "")
    info["Цвет"] = info.get("Цвет", data.get("color", ""))

    # Пустые поля, которых нет в API (можно потом добить из parser.py)
    info["Вид рыбы"] = ""
    info["Спортивное назначение"] = ""

    return info
