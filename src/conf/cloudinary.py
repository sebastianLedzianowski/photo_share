from random import choice

import cloudinary
from src.services.secrets_manager import SecretsManager
import string

CLOUDINARY_NAME = SecretsManager.get_secret("CLOUDINARY_NAME")
CLOUDINARY_API_KEY = SecretsManager.get_secret("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = SecretsManager.get_secret("CLOUDINARY_API_SECRET")


def configure_cloudinary():

    config = cloudinary.config(
                cloud_name=CLOUDINARY_NAME,
                api_key=CLOUDINARY_API_KEY,
                api_secret=CLOUDINARY_API_SECRET,
                secure=True
            )

    return config


def generate_random_string(length=30):
    """Generate a random alpha-numeric string of the specified length."""
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(choice(letters_and_digits) for _ in range(length))
