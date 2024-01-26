import requests
import secrets
from weasyprint import HTML
from django.conf import settings
from django.core.mail import EmailMessage


def telegram_pusher(code: str, user, expires_in):
    text = (f"{user.phone_number} was registered.\n"
            f"Verification Code: {code}\n"
            f"Expires time: {expires_in}")

    url = f"https://api.telegram.org/bot{settings.VERIFICATION_BOT_TOKEN}/sendMessage?chat_id={settings.CHANNEL_ID}&text=%s"
    requests.get(url=url % text)


def generate_code():
    numbers = "123456789"
    return "".join(secrets.choice(numbers) for i in range(6))


def convert_text_to_pdf(file_name: str):
    html = HTML(filename="bot/templates/applicant_info.html", encoding="utf-8")
    html.write_pdf(target=file_name)
    return file_name


def email_sender(file_name):
    email = EmailMessage(
        subject="Job Application",
        body="Job Application",
        from_email=settings.EMAIL_HOST_USER,
        to=[settings.EMAIL_SEND_TO_USER],
    )
    email.attach_file(file_name)
    email.send()
    return True


def document_pusher(file):
    url = f"https://api.telegram.org/bot{settings.VERIFICATION_BOT_TOKEN}/sendDocument?chat_id={settings.CHANNEL_ID}"
    files = {"document": open(file, "rb")}
    requests.post(url=url, files=files)
