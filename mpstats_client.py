# mpstats_client.py

import os
import logging
import requests
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

API_TOKEN = os.getenv("MPSTATS_API_TOKEN")
BASE_URL = "https://mpstats.io/api/wb/get"

def get_versions(sku: str, d1: str, d2: str) -> list:
    """
    Возвращает историю версий товара по SKU за период [d1, d2].
    """
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

    # 2) Запрос подробной страницы по этой версии
    url = f"{BASE_URL}/item/{sku}/full_page"
    params = {"version": latest}
    headers = {"X-Mpstats-TOKEN": API_TOKEN} if API_TOKEN else {}
    logger.debug(f"Request to MPSTATS product: {url} params={params}")
    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    logger.info(f"Full page data for {sku}: {data}")

    # 3) Парсим поля (ключи зависит от формата ответа API!)
    # В примере ниже я условно беру поля из data["product_info"]
    info = data.get("product_info", {})

    return {
        "sku":                          sku,
        "Наименование":                 info.get("name", ""),
        "Длина":                        info.get("length", ""),
        "Толщина лески":                info.get("thickness", ""),
        "Вид лески":                    info.get("type", ""),
        "Материал лески":               info.get("material", ""),
        "Максимальная нагрузка":        info.get("max_load", ""),
        "Вид рыбы":                     info.get("fish_type", ""),
        "Спортивное назначение":        info.get("sport_usage", ""),
        "Цвет":                         info.get("color", ""),
    }

