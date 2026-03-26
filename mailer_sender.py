import os
import smtplib
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from database import connect_mongodb
from email_builder import build_email_template
from sheets_service import get_sheet_by_name, get_sheets_service

CREDENTIALS_FILE = "pesquisa-do-sono-a3a901e3c4d5.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

CONTACT_SHEET_ID = "1v3lohzmJL7L2bh9W_1l1_r9Ryr8ChJPe9-AA26KyQZU"
ANSWERS_SHEET_ID = "1nOIkumaZmelCZeI9SQcjsGMxsdnObSsPM5dyQQNiasY"
CONTACT_SHEET_TAB_NAME = "Respostas ao formulário 0"
ANSWERS_SHEET_TAB_1 = "Respostas ao formulário 1"
ANSWERS_SHEET_TAB_2 = "Respostas ao formulário 2"
ANSWERS_SHEET_TAB_3 = "Respostas ao formulário 3"
ANSWERS_SHEET_TAB_4 = "Respostas ao formulário 4"
ANSWERS_SHEET_TAB_5 = "Respostas ao formulário 5"
ANSWERS_SHEET_TAB_6 = "Respostas ao formulário 6"
ANSWERS_SHEET_TAB_7 = "Respostas ao formulário 7"
ANSWERS_SHEET_TAB_8 = "Respostas ao formulário 8"
ANSWERS_SHEET_TAB_9 = "Respostas ao formulário 9"
ANSWERS_SHEET_TAB_10 = "Respostas ao formulário 10"
ANSWERS_SHEET_TAB_11 = "Respostas ao formulário 11"

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

FORM_URL1 = "https://docs.google.com/forms/d/e/1FAIpQLScAkak8r2lIwrIXpD8r890byiNagGe5KyZ_AWIPkH0d_kZgSg/viewform?usp=sharing"
FORM_URL2 = "https://docs.google.com/forms/d/e/1FAIpQLScHElxFlk52MgPrNDfNNBD1f7ow6EX0h-uZKmjt4p_jsWfuBQ/viewform?usp=sharing"
FORM_URL3 = "https://docs.google.com/forms/d/e/1FAIpQLSe78Uptu9OR5C8bbK6orbiitKzny2Fa2WVEsBg3JwSTqvnhDg/viewform?usp=sharing"
FORM_URL4 = "https://docs.google.com/forms/d/e/1FAIpQLSdFFnwU6y_JUPjLmFjRcEnTNu0d89FH1oDVdMtLqKl_xLU8nA/viewform?usp=sharing"
FORM_URL5 = "https://docs.google.com/forms/d/e/1FAIpQLSdoNoTnBhOv25MqsR6Kxh6NSYL1MEpzgwhjlNcf-0b1w2EXPA/viewform?usp=sharing"
FORM_URL6 = "https://docs.google.com/forms/d/e/1FAIpQLScmOct9lSvNktdVSA8p7pOI9DOd30sSMilRhEJHtM_MugToPA/viewform?usp=sharing"
FORM_URL7 = "https://docs.google.com/forms/d/e/1FAIpQLSfWz3n6nOGqMr7wyI0OVxbY8v87LkSODhVAsRvFrsLsAwCwiQ/viewform?usp=sharing"
FORM_URL8 = "https://docs.google.com/forms/d/e/1FAIpQLSc_SugIwE5paDCE52D2NlzNjhSm4wwFUUDY1np3vZ79aN-8ig/viewform?usp=sharing"
FORM_URL9 = "https://docs.google.com/forms/d/e/1FAIpQLSfGd3QZ5voBTgnShTZwX55r61ranQFZNcSdxwKCjRe6PQk5qA/viewform?usp=sharing"
FORM_URL10 = "https://docs.google.com/forms/d/e/1FAIpQLScRsh7WvPyK5aBATJb5TkVusQ2-W5FdhGHC-Jko65b6T1uXZw/viewform?usp=sharing"
FORM_URL11 = "https://docs.google.com/forms/d/e/1FAIpQLScbE6bW7VwANVNds5oAifPJ90B6OHa8JmkU6E_-GGcIhx-SwQ/viewform?usp=sharing"

from datetime import datetime


def last_answer_by_user(email, all_tabs):
    def parse_date(value):
        try:
            return datetime.strptime(value, "%d/%m/%Y %H:%M:%S").date()
        except ValueError:
            try:
                return datetime.strptime(value, "%d/%m/%Y").date()
            except ValueError:

                return None

    latest_row = None
    latest_date = None

    for row in all_tabs:
        if row.get("email") != email:
            continue

        date_str = row.get("data/hora")
        if not date_str:
            continue

        current_date = parse_date(date_str)
        if not current_date:
            continue

        if latest_date is None or current_date > latest_date:
            latest_date = current_date
            latest_row = row

    return latest_row


def is_within_allowed_range(last_answer_date_str):
    def parse_date(value):
        try:
            return datetime.strptime(value, "%d/%m/%Y %H:%M:%S").date()
        except ValueError:
            try:
                return datetime.strptime(value, "%d/%m/%Y").date()
            except ValueError:
                return False

    last_date = parse_date(last_answer_date_str)
    if not last_date:
        return False

    base_date = last_date + relativedelta(months=1)
    today = datetime.today().date()

    return base_date <= today <= (base_date + timedelta(days=2))


def get_form_url_by_status(email, tabs):
    last_answer = last_answer_by_user(email, tabs)

    if not last_answer:
        return None

    is_allowed = is_within_allowed_range(last_answer.get("data/hora"))

    if not is_allowed:
        return None

    sheet_to_form_url = {
        CONTACT_SHEET_TAB_NAME: FORM_URL1,
        ANSWERS_SHEET_TAB_1: FORM_URL2,
        ANSWERS_SHEET_TAB_2: FORM_URL3,
        ANSWERS_SHEET_TAB_3: FORM_URL4,
        ANSWERS_SHEET_TAB_4: FORM_URL5,
        ANSWERS_SHEET_TAB_5: FORM_URL6,
        ANSWERS_SHEET_TAB_6: FORM_URL7,
        ANSWERS_SHEET_TAB_7: FORM_URL8,
        ANSWERS_SHEET_TAB_8: FORM_URL9,
        ANSWERS_SHEET_TAB_9: FORM_URL10,
        ANSWERS_SHEET_TAB_10: FORM_URL11,
        ANSWERS_SHEET_TAB_11: FORM_URL11,
    }

    return sheet_to_form_url.get(last_answer.get("sheet"))


def log_submissions(emails_sent_collection, email, form, message="Sucesso"):
    try:
        log_entry = {
            "email": email,
            "form": form,
            "message": message,
            "sent_at": datetime.now(),
        }
        emails_sent_collection.insert_one(log_entry)

    except Exception as e:
        print(f"Erro ao registrar log de envio para: {email}: {e}")


def send_email(server, email, form_url, logs_collection):
    try:
        msg = build_email_template(email, form_url)
        server.send_message(msg)

        print(f"E-mail enviado para {email}")
        log_submissions(logs_collection, email, form_url)

    except Exception as e:
        print(f"Erro ao enviar e-mail para {email}: {e}")
        log_submissions(logs_collection, email, form_url, f"Erro: {e}")


def mailer_sender():
    print("Autenticando no servidor...")
    client, db = connect_mongodb()
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    sheets_service = get_sheets_service()

    print("Lendo planilhas...")
    users = get_sheet_by_name(sheets_service, CONTACT_SHEET_ID, CONTACT_SHEET_TAB_NAME)
    tab1 = get_sheet_by_name(sheets_service, ANSWERS_SHEET_ID, ANSWERS_SHEET_TAB_1)
    tab2 = get_sheet_by_name(sheets_service, ANSWERS_SHEET_ID, ANSWERS_SHEET_TAB_2)
    tab3 = get_sheet_by_name(sheets_service, ANSWERS_SHEET_ID, ANSWERS_SHEET_TAB_3)
    tab4 = get_sheet_by_name(sheets_service, ANSWERS_SHEET_ID, ANSWERS_SHEET_TAB_4)
    tab5 = get_sheet_by_name(sheets_service, ANSWERS_SHEET_ID, ANSWERS_SHEET_TAB_5)
    tab6 = get_sheet_by_name(sheets_service, ANSWERS_SHEET_ID, ANSWERS_SHEET_TAB_6)
    tab7 = get_sheet_by_name(sheets_service, ANSWERS_SHEET_ID, ANSWERS_SHEET_TAB_7)
    tab8 = get_sheet_by_name(sheets_service, ANSWERS_SHEET_ID, ANSWERS_SHEET_TAB_8)
    tab9 = get_sheet_by_name(sheets_service, ANSWERS_SHEET_ID, ANSWERS_SHEET_TAB_9)
    tab10 = get_sheet_by_name(sheets_service, ANSWERS_SHEET_ID, ANSWERS_SHEET_TAB_10)
    tab11 = get_sheet_by_name(sheets_service, ANSWERS_SHEET_ID, ANSWERS_SHEET_TAB_11)

    if not users:
        print("Nenhum usuário encontrado. processamento encerrado.")
        client.close()
        return

    for user in users:
        email = user.get("email")
        all_tabs = [
            *(tab1 or []),
            *(tab2 or []),
            *(tab3 or []),
            *(tab4 or []),
            *(tab5 or []),
            *(tab6 or []),
            *(tab7 or []),
            *(tab8 or []),
            *(tab9 or []),
            *(tab10 or []),
            *(tab11 or []),
            *(users or []),
        ]

        form_url = get_form_url_by_status(email, all_tabs)

        if not form_url:
            continue

        send_email(server, email, form_url, db['logs'])

    server.quit()
    client.close()
    print("Processo de envio concluído.")
