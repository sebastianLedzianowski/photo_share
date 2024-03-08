import cloudinary
from src.services.secrets_manager import get_secret

CLOUDINARY_NAME = get_secret("CLOUDINARY_NAME")
CLOUDINARY_API_KEY = get_secret("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = get_secret("CLOUDINARY_API_SECRET")


def configure_cloudinary():

    config = cloudinary.config(
                cloud_name=CLOUDINARY_NAME,
                api_key=CLOUDINARY_API_KEY,
                api_secret=CLOUDINARY_API_SECRET,
                secure=True
            )

    return config
