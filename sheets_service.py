import json
import os

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

CREDENTIALS_FILE = "pesquisa-do-sono-a3a901e3c4d5.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def get_sheets_service():
    credentials_info = json.loads(os.getenv("G_CREDENTIALS"))

    credentials = Credentials.from_service_account_info(
        credentials_info,
        scopes=SCOPES,
    )
    return build("sheets", "v4", credentials=credentials)


def get_sheets_names(sheets_service, form_id):
    spreadsheet = sheets_service.spreadsheets().get(
        spreadsheetId=form_id
    ).execute()

    sheets = spreadsheet.get("sheets", [])

    if not sheets:
        raise ValueError("A planilha não possui abas disponíveis.")

    return sheets


def get_sheet_by_name(sheets_service, form_id, sheet_name):
    sheets = get_sheets_names(sheets_service, form_id)

    for sheet in sheets:
        properties = sheet.get("properties", {})
        if properties.get("title") == sheet_name:
            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=form_id,
                range=f"{sheet_name}!A:Z",
            ).execute()

            values = result.get("values", [])

            if len(values) < 1:
                return []

            headers = values[0]
            rows = values[1:]
            structured_rows = []

            for row in rows:
                row_dict = dict(zip(headers, row))
                structured_rows.append({
                    "sheet": sheet_name,
                    "data/hora": row_dict.get("Carimbo de data/hora"),
                    "email": row_dict.get("Endereço de e-mail"),
                })

            return structured_rows

    raise ValueError(f"A aba '{sheet_name}' não foi encontrada na planilha.")
