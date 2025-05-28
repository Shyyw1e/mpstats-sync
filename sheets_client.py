import os
import logging
from google_auth import get_sheets_service

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

    def write_rows(self, sheet_name: str, start_row: int, rows: list):
        start_cell = f"A{start_row}"
        logger.debug(f"Writing {len(rows)} rows to '{sheet_name}' at {start_cell}")
        self.values.update(
            spreadsheetId=self.spreadsheet_id,
            range=f"{sheet_name}!{start_cell}",
            valueInputOption="RAW",
            body={"values": rows}
        ).execute()

    def _get_sheet_id(self, sheet_name: str) -> int:
        meta = self.spreadsheets.get(  # снова — как атрибут
            spreadsheetId=self.spreadsheet_id
        ).execute()
        for s in meta.get("sheets", []):
            props = s.get("properties", {})
            if props.get("title") == sheet_name:
                return props.get("sheetId")
        raise ValueError(f"Sheet '{sheet_name}' not found")
