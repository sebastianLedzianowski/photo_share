from fastapi import requests

import requests
from pydantic import EmailStr

from src.services.secrets_manager import get_secret
from src.services.auth import auth_service

MAILGUN_API_KEY = get_secret("MAILGUN_API_KEY")
MAILGUN_DOMAIN = get_secret("MAILGUN_DOMAIN")
MAILGUN_ENDPOINT = f'https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages'

async def send_email(email: EmailStr,
                     subject: str,
                     email_content: str) -> None:
    """
    Send email using Mailgun.

    Args:
        email (EmailStr): The recipient's email address.
        subject (str): The subject of the email.
        email_content (str): Path to the email message.
    """
    response = requests.post(
        MAILGUN_ENDPOINT,
        auth=("api", MAILGUN_API_KEY),
        data={
            "from": f"Photo_Share <mail@{MAILGUN_DOMAIN}>",
            "to": [email],
            "subject": subject,
            "text": email_content
        }
    )
    response.raise_for_status()

async def send_verification_email(email: str, host: str) -> None:
    """
    Send email with a verification token link for email confirmation.

    Args:
        email (str): The recipient's email address.
        host (str): The base URL for the application.

    Raises:
        ConnectionErrors: If there is an error connecting to the mail server.
    """
    subject = "Confirm your email"
    token = auth_service.create_email_token({"sub": email})
    email_content = f"Hello\nThank you for registering.\nPlease click the link below to verify your email:\n{host}api/auth/confirmed_email/{token}\nIf you didn't register, you can ignore this email."

    await send_email(email=email, subject=subject, email_content=email_content)


async def send_reset_email(email: str, host: str) -> None:
    """
    Send email with a password reset token link.

    Args:
        email (str): The recipient's email address.
        host (str): The base URL for the application.

    Raises:
        ConnectionErrors: If there is an error connecting to the mail server.
    """
    subject = "Password Reset Request"
    token = auth_service.create_email_token({"sub": email})
    email_content = f"Hello\nYou requested a password reset.\nClick the link below to reset your password:\n{host}api/auth/reset_password/{token}\nIf you didn't request a password reset, you can ignore this email."

    await send_email(email=email, subject=subject, email_content=email_content)
