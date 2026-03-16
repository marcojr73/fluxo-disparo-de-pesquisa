from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from database import connect_mongodb

CREDENTIALS_FILE = "iron-stack-450320-s7-c56aa0b23bf7.json"
NEW_USERS_SHEET_ID = "1Nknx9qjcriOUARndNqyKxlMoVla0WOEsEoe_Obn-k2A"
CONTACT_SHEET_ID = "1B-mWUXVhlpeYId_M5e7xjwjzgJyzFGe899LL22LDHu4"
ANSWERS_SHEET_ID = "1CHXXWUw1AkrpiKtYdrrqgbvcX1p6gzkLHU-Tc4dnt6Y"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
USERS_COLLECTION = "users"
NEW_USERS_COLLECTION = "new-users"


def _get_sheets_service():
    credentials = Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
    )
    return build("sheets", "v4", credentials=credentials)


def _get_sheets_name(sheets_service, form_id):
    spreadsheet = sheets_service.spreadsheets().get(
        spreadsheetId=form_id
    ).execute()

    sheets = spreadsheet.get("sheets", [])

    if not sheets:
        raise ValueError("A planilha não possui abas disponíveis.")

    return [sheet["properties"]["title"] for sheet in sheets]


def update_status(sheet_name, rows):
    if not sheet_name.startswith("Perguntas "):
        return

    sheet_number_text = sheet_name.replace("Perguntas ", "").strip()

    if not sheet_number_text.isdigit():
        return

    sheet_number = int(sheet_number_text)

    if sheet_number < 1 or sheet_number >= 10:
        return

    new_status = str(sheet_number + 1)
    emails = [
        row.get("e-mail")
        for row in rows
        if row.get("e-mail")
    ]

    if not emails:
        return

    client, db = connect_mongodb()

    try:
        users_collection = db[USERS_COLLECTION]
        result = users_collection.update_many(
            {"email": {"$in": emails}},
            {"$set": {"status": new_status}},
        )
        print(
            f"Status atualizado para {new_status} em "
            f"{result.modified_count} usuário(s) da aba {sheet_name}."
        )
    finally:
        client.close()


def _persist_form_data(tab_name, structured_rows, users_collection):
    users_collection.delete_many({})
    if structured_rows:
        users_collection.insert_many(structured_rows)
    print(f"Respostas da aba {tab_name} salvas com sucesso.")


def _read_form(sheets_service, form_id, tab_name):
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=form_id,
        range=f"{tab_name}!A:Z",
    ).execute()

    values = result.get("values", [])

    if len(values) < 2:
        print(f"Nenhum dado encontrado na aba {tab_name}.")
        return []

    headers = values[0]
    rows = values[1:]

    structured_rows = []

    for row in rows:
        row_dict = dict(zip(headers, row))
        structured_rows.append({
            "e-mail": row_dict.get("Endereço de e-mail"),
            "data/hora": row_dict.get("Carimbo de data/hora"),
        })

    return structured_rows


def persist_new_users(sheets_service, new_users_collection):
    users_sheet = _get_sheets_name(sheets_service, NEW_USERS_SHEET_ID)[0]
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=NEW_USERS_SHEET_ID,
        range=f"{users_sheet}!A:Z",
    ).execute()

    values = result.get("values", [])

    if len(values) < 2:
        print(f"Nenhum dado encontrado na aba {values}.")
        return []
    rows = values

    for row in rows:
        print(f"row: {row[0]}")
        new_users_collection.delete_many({})
        new_users_collection.insert_many({
            'email': row[0],
            'status': 'novo'
        })
    return None


def update_answers():
    print("Atualizando respostas...")
    client, db = connect_mongodb()

    try:
        sheets_service = _get_sheets_service()
        persist_new_users(sheets_service, db[NEW_USERS_COLLECTION])
        contact_sheet = _get_sheets_name(sheets_service, CONTACT_SHEET_ID)[0]
        answers_sheets = _get_sheets_name(sheets_service, ANSWERS_SHEET_ID)

        contact_rows = _read_form(sheets_service, CONTACT_SHEET_ID, contact_sheet)
        _persist_form_data(contact_sheet, contact_rows, db[USERS_COLLECTION])

        for sheet_name in answers_sheets:
            structured_rows = _read_form(sheets_service, ANSWERS_SHEET_ID, sheet_name)
            _persist_form_data(sheet_name, structured_rows, db[USERS_COLLECTION])
            update_status(sheet_name, structured_rows)

    except Exception as e:
        print(f"Erro ao ler a planilha: {e}")
