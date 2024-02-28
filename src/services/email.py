from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.secrets_manager import get_secret
from src.services.auth import auth_service

MAIL_USERNAME = get_secret("MAIL_USERNAME")
MAIL_PASSWORD = get_secret("MAIL_PASSWORD")
MAIL_FROM = get_secret("MAIL_FROM")
MAIL_PORT = get_secret("MAIL_PORT")
MAIL_SERVER = get_secret("MAIL_SERVER")
MAIL_STARTTLS = get_secret("MAIL_STARTTLS")
MAIL_SSL_TLS = get_secret("MAIL_SSL_TLS")
USE_CREDENTIALS = get_secret("USE_CREDENTIALS")
VALIDATE_CERTS = get_secret("VALIDATE_CERTS")

conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_FROM_NAME=MAIL_FROM,
    MAIL_STARTTLS=MAIL_STARTTLS,
    MAIL_SSL_TLS=MAIL_SSL_TLS,
    USE_CREDENTIALS=USE_CREDENTIALS,
    VALIDATE_CERTS=VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)

async def send_email(email: EmailStr, username: str, host: str) -> None:
    """
    Send email with a verification token link for email confirmation.

    Args:
        email (EmailStr): The recipient's email address.
        username (str): The username of the recipient.
        host (str): The base URL for the application.

    Raises:
        ConnectionErrors: If there is an error connecting to the mail server.
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)

async def send_verification_email(email: str, username: str, host: str) -> None:
    """
    Send email with a verification token link for email confirmation.

    Args:
        email (str): The recipient's email address.
        username (str): The username of the recipient.
        host (str): The base URL for the application.

    Raises:
        ConnectionErrors: If there is an error connecting to the mail server.
    """
    subject = "Confirm your email"
    verification_token = auth_service.create_email_token({"sub": email})
    message = f"Click the following link to confirm your email: {host}/verify-email?token={verification_token}"

    await send_email(email, subject, message)


async def send_reset_email(email: str, reset_token: str, host: str) -> None:
    """
    Send email with a password reset token link.

    Args:
        email (str): The recipient's email address.
        reset_token (str): The password reset token.
        host (str): The base URL for the application.

    Raises:
        ConnectionErrors: If there is an error connecting to the mail server.
    """
    subject = "Password Reset Request"
    message = f"Click the following link to reset your password: {host}/reset-password?token={reset_token}"

    await send_email(email, subject, message)