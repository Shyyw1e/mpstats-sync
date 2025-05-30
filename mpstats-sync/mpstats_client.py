from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import os
import re
import logging
import requests


logger = logging.getLogger(__name__)

API_TOKEN = os.getenv("MPSTATS_API_TOKEN")
BASE_URL = "https://mpstats.io/api/wb/get"

# Финальное отображение нужных полей
TARGET_FIELDS = [
    "sku",
    "Наименование",
    "Длина",
    "Толщина лески",
    "Вид лески",
    "Материал лески",
    "Максимальная нагрузка",
    "Вид рыбы",
    "Спортивное назначение",
    "Цвет"
]

# Сопоставление вариантов названий с нужным полем
FIELD_MAPPING = {
    "Толщина лески": "Толщина лески",
    "Толщина (мм)": "Толщина лески",
    "Толщина": "Толщина лески",
    "Диаметр": "Толщина лески",
    "Диаметр лески": "Толщина лески",

    "Длина (м)": "Длина",
    "Длина": "Длина",
    "Метраж": "Длина",
    "Намотка": "Длина",
    "Длина намотки": "Длина",

    "Вид лески": "Вид лески",
    "Материал лески": "Материал лески",
    "Максимальная нагрузка": "Максимальная нагрузка",
    "Цвет": "Цвет"
}

def normalize(text: str) -> str:
    return text.lower().replace("ё", "е").strip()

def extract_param_value(param_names, param_values, target_field):
    """Ищет значение по синонимам поля"""
    value = ""
    for name, val in zip(param_names, param_values):
        for source_key, mapped_field in FIELD_MAPPING.items():
            if mapped_field == target_field and normalize(source_key) in normalize(name):
                value = val.strip()
                # Приводим к нужному виду, если это числовое значение
                if target_field == "Толщина лески" and not re.search(r"мм", value, flags=re.IGNORECASE):
                    # Если цифры и нет "мм" — добавим
                    if re.search(r"\d", value):
                        value = value.replace(",", ".") + " мм"
                return value
    return value

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
    latest = versions[0].get("version") if versions else ""

    url = f"{BASE_URL}/item/{sku}/full_page"
    params = {"version": latest}
    headers = {"X-Mpstats-TOKEN": API_TOKEN} if API_TOKEN else {}
    logger.debug(f"Request to MPSTATS product: {url} params={params}")
    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    logger.info(f"Full page data for {sku}: {data}")

    param_names = data.get("param_names", [])
    param_values = data.get("param_values", [])

    info = {
        "sku": sku,
        "Наименование": data.get("full_name", ""),
        "Цвет": data.get("color", ""),
        "Вид рыбы": "",
        "Спортивное назначение": ""
    }

    # Извлекаем нужные значения по маппингу
    for target_field in TARGET_FIELDS:
        if target_field in info:
            continue  # уже заполнено выше
        info[target_field] = extract_param_value(param_names, param_values, target_field)

    # Fallback: толщина из наименования, если не нашли
    if not info["Толщина лески"]:
        name = info["Наименование"]
        match = re.search(r"([0,\.]{0,1}\d{1,2}[.,]\d{1,2})\s*мм", name, flags=re.IGNORECASE)
        if match:
            value = match.group(1).replace(",", ".")
            info["Толщина лески"] = f"{value} мм"

    return info
