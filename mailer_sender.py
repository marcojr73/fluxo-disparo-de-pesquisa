import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from database import connect_mongodb

USERS_COLLECTION = 'users'
SUBMISSIONS_COLLECTION = 'e-mails-sent'

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

FORM_URL0 = "https://forms.gle/Md8zJoWEEvk5bLrf8"
FORM_URL1 = "https://forms.gle/dYs1cQ7HZpExv1rT6"
FORM_URL2 = "https://forms.gle/EwccT2aCdyKnQfQcA"


def get_all_users(users_collection):
    recipients = []

    try:
        users = users_collection.find()

        for user in users:
            email = user.get("email")
            if email:
                recipients.append(user)

    except Exception as e:
        print(f"Erro ao buscar usuários no MongoDB: {e}")

    return recipients


def get_form_url_by_status(status):
    status_form_map = {
        "novo": FORM_URL0,
        "1": FORM_URL1,
        "2": FORM_URL2,
    }

    return status_form_map.get(str(status))


def log_submissions(emails_sent_collection, user_id, email):
    try:
        log_entry = {
            "user_id": user_id,
            "email": email,
            "sent_at": datetime.now(),
            "status": "sucesso"
        }
        emails_sent_collection.insert_one(log_entry)
        print(f"Log de envio registrado para {email}.")

    except Exception as e:
        print(f"Erro ao registrar log de envio: {e}")


def create_email(recipient_email, form_url):
    msg = MIMEMultipart()

    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email
    msg["Subject"] = "Avaliação do Sono - Formulário de Pesquisa"

    body = f"""Olá,

Gostaríamos de contar com sua participação na nossa Avaliação do Sono.
Preencha o formulário no link abaixo:
{form_url}

Atenciosamente,
Equipe Avaliação do Sono
"""

    msg.attach(MIMEText(body, "plain"))
    return msg


def send_email(server, recipient_email, form_url):
    try:
        msg = create_email(recipient_email, form_url)
        server.send_message(msg)

        print(f"E-mail enviado para {recipient_email}")
        return True

    except Exception as e:
        print(f"Erro ao enviar e-mail para {recipient_email}: {e}")
        return False


def mailer_sender():
    print("Iniciando disparo de e-mails...")
    client, db = connect_mongodb()
    users_collection = db[USERS_COLLECTION]
    emails_sent_collection = db[SUBMISSIONS_COLLECTION]
    recipients = get_all_users(users_collection)

    if not recipients:
        print("Nenhum usuário encontrado.")
        client.close()
        return

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)

    for user in recipients:
        email = user.get("email")
        user_id = user.get("_id")
        status = user.get("status")
        form_url = get_form_url_by_status(status)

        if not email:
            continue

        if not form_url:
            print(f"Status '{status}' não possui formulário configurado para o usuário {email}.")
            continue

        sent = send_email(server, email, form_url)

        if sent:
            log_submissions(emails_sent_collection, user_id, email)

    server.quit()
    client.close()
    print("Processo de envio concluído.")
