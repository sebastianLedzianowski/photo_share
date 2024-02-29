from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    """
    Configuration settings for the application.

    Attributes:
        secret_name (str): The name of the secret.
        region_name (str): The AWS region name.
        aws_access_key_id (str): The AWS access key ID.
        aws_secret_access_key (str): The AWS secret access key.

    Config:
        env_file (str): The path to the environment file.
        env_file_encoding (str): The encoding of the environment file.
    """
    secret_name: str
    region_name: str
    aws_access_key_id: str
    aws_secret_access_key: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
