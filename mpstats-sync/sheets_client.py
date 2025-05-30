from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import os
import logging
from google_auth import get_sheets_service
import time

logger = logging.getLogger(__name__)

class SheetsClient:
    def __init__(self, spreadsheet_id: str = None):
        # получаем service из google_auth
        self.service = get_sheets_service()
        # В твоём случае у service есть атрибут spreadsheets, а не метод spreadsheets()
        self.spreadsheets = self.service.spreadsheets()
        self.values = self.spreadsheets.values()
        self.spreadsheet_id = spreadsheet_id or os.getenv("SPREADSHEET_ID")

    def ensure_headers(self, sheet_name: str, headers: list):
        sheet_id = self._get_sheet_id(sheet_name)
        body = {
            "requests": [{
                "updateCells": {
                    "start": {"sheetId": sheet_id, "rowIndex": 0, "columnIndex": 0},
                    "rows": [{
                        "values": [
                            {"userEnteredValue": {"stringValue": h}}
                            for h in headers
                        ]
                    }],
                    "fields": "userEnteredValue"
                }
            }]
        }
        # Теперь обращаемся к атрибуту, а не к несуществующему методу
        self.spreadsheets.batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=body
        ).execute()

    def read_column(self, sheet_name: str, header: str) -> list:
        first_row = self.values.get(
            spreadsheetId=self.spreadsheet_id,
            range=f"{sheet_name}!1:1"
        ).execute().get("values", [[]])[0]
        try:
            idx = first_row.index(header)
        except ValueError:
            logger.warning(f"Header '{header}' not found in '{sheet_name}'")
            return []
        col = chr(ord("A") + idx)
        vals = self.values.get(
            spreadsheetId=self.spreadsheet_id,
            range=f"{sheet_name}!{col}2:{col}"
        ).execute().get("values", [])
        return [row[0] for row in vals if row]

    import time

    def write_rows(self, sheet_name: str, start_row: int, rows: list):
        batch_size = 100  # ↓ уменьшили
        total = len(rows)
        logger.info(f"Запись {total} строк в таблицу '{sheet_name}' порциями по {batch_size}")

        for i in range(0, total, batch_size):
            chunk = rows[i:i + batch_size]
            row_num = start_row + i
            start_cell = f"A{row_num}"
            logger.info(f"Пишем строки {row_num} — {row_num + len(chunk) - 1}")

            # retry-петля
            for attempt in range(3):
                try:
                    self.values.update(
                        spreadsheetId=self.spreadsheet_id,
                        range=f"{sheet_name}!{start_cell}",
                        valueInputOption="RAW",
                        body={"values": chunk}
                    ).execute()
                    break  # успешно — выходим из retry
                except Exception as e:
                    logger.warning(
                        f"Попытка {attempt + 1}/3: ошибка при записи строк {row_num}-{row_num + len(chunk) - 1}: {e}")
                    if attempt == 2:
                        raise
                    time.sleep(2)

            # пауза между чанками
            if i + batch_size < total:
                logger.debug("Ожидание 1 сек перед следующим блоком...")
                time.sleep(1)

    def _get_sheet_id(self, sheet_name: str) -> int:
        meta = self.spreadsheets.get(  # снова — как атрибут
            spreadsheetId=self.spreadsheet_id
        ).execute()
        for s in meta.get("sheets", []):
            props = s.get("properties", {})
            if props.get("title") == sheet_name:
                return props.get("sheetId")
        raise ValueError(f"Sheet '{sheet_name}' not found")
