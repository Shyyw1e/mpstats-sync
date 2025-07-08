from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import os
import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

API_TOKEN = os.getenv("MPSTATS_API_TOKEN")
BASE_URL = "https://mpstats.io/api/wb/get"

TARGET_FIELDS = [
    "sku", "Наименование", "Вид воблера", "Вид крючка", "Плавучесть",
    "Вес товара без упаковки (г)", "Длина предмета (см)", "Максимальное заглубление",
    "Минимальное заглубление", "Комплектация", "Спортивное назначение", "Цвет"
]

FIELD_MAPPING = {
    "Наименование": "Наименование",
    "Вид воблера": "Вид воблера",
    "Тип воблера": "Вид воблера",
    "Вид крючка": "Вид крючка",
    "Плавучесть": "Плавучесть",
    "Вес товара без упаковки": "Вес товара без упаковки (г)",
    "Длина предмета": "Длина предмета (см)",
    "Длина": "Длина предмета (см)",
    "Максимальное заглубление": "Максимальное заглубление",
    "Минимальное заглубление": "Минимальное заглубление",
    "Комплектация": "Комплектация",
    "Спортивное назначение": "Спортивное назначение",
    "Цвет": "Цвет"
}

def normalize(text: str) -> str:
    return text.lower().replace("ё", "е").strip()

def extract_param_value(param_names, param_values, target_field):
    for name, val in zip(param_names, param_values):
        for key, mapped_field in FIELD_MAPPING.items():
            if mapped_field == target_field and normalize(key) in normalize(name):
                return val.strip()
    return ""

def get_versions(sku: str, d1: str, d2: str) -> list:
    url = f"{BASE_URL}/item/{sku}/full_page/versions"
    params = {"d1": d1, "d2": d2}
    headers = {"X-Mpstats-TOKEN": API_TOKEN} if API_TOKEN else {}
    logger.debug(f"Request to MPSTATS versions: {url} params={params}")
    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()
    return resp.json()

def get_wobbler_info(sku: str, d1: str, d2: str) -> dict:
    versions = get_versions(sku, d1, d2)
    latest = versions[0].get("version") if versions else ""

    url = f"{BASE_URL}/item/{sku}/full_page"
    params = {"version": latest}
    headers = {"X-Mpstats-TOKEN": API_TOKEN} if API_TOKEN else {}
    logger.debug(f"Request to MPSTATS product: {url} params={params}")
    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    logger.info(f"Full page data for reel {sku}: {data}")

    param_names = data.get("param_names", [])
    param_values = data.get("param_values", [])

    info = {"sku": sku}
    for field in TARGET_FIELDS:
        if field == "sku":
            continue
        info[field] = extract_param_value(param_names, param_values, field)

    return info

