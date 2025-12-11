import smtplib, os
from email.message import EmailMessage
from twilio.rest import Client
from .config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, TWILIO_SID, TWILIO_TOKEN, TWILIO_FROM

def send_email_smtp(to:str, subject:str, body:str):
    if not SMTP_USER or not SMTP_PASS:
        return False, "SMTP not configured"
    try:
        msg = EmailMessage()
        msg["From"] = SMTP_USER
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True, "sent"
    except Exception as e:
        return False, str(e)

def send_sms_twilio(to, body):
    if not TWILIO_SID or not TWILIO_TOKEN or not TWILIO_FROM:
        return {"ok": False, "error":"Twilio not configured"}
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    try:
        msg = client.messages.create(body=body, from_=TWILIO_FROM, to=to)
        return {"ok": True, "sid": msg.sid}
    except Exception as e:
        return {"ok": False, "error": str(e)}

