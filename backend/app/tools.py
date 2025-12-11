# app/tools.py
import smtplib
from email.message import EmailMessage
from twilio.rest import Client
from app.config import settings
import logging

logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, body: str):
    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASS or not settings.EMAIL_FROM:
        raise RuntimeError("SMTP not configured.")
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email
    msg.set_content(body)
    server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
    server.starttls()
    server.login(settings.SMTP_USER, settings.SMTP_PASS)
    server.send_message(msg)
    server.quit()
    logger.info("Email sent to %s", to_email)

def send_sms(to_number: str, body: str):
    if not settings.TWILIO_SID or not settings.TWILIO_TOKEN or not settings.TWILIO_FROM:
        raise RuntimeError("Twilio not configured.")
    client = Client(settings.TWILIO_SID, settings.TWILIO_TOKEN)
    msg = client.messages.create(body=body, from_=settings.TWILIO_FROM, to=to_number)
    logger.info("SMS sent: %s", msg.sid)
    return msg.sid
