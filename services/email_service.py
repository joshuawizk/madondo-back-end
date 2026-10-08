import os
import smtplib
from email.message import EmailMessage


def send_email(to_address, subject, body, from_name="Madondo Hope Foundation"):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from_email = os.getenv("SMTP_FROM_EMAIL", "noreply@madondo.org")
    smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

    if not smtp_host or not smtp_username or not smtp_password:
        return {
            "success": False,
            "message": "SMTP settings are not configured for outbound email delivery.",
        }

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"{from_name} <{smtp_from_email}>"
    message["To"] = to_address
    message.set_content(body)

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            if smtp_use_tls:
                server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(message)
        return {
            "success": True,
            "message": "Email queued successfully.",
        }
    except Exception as exc:
        return {
            "success": False,
            "message": f"Unable to send email: {exc}",
        }
