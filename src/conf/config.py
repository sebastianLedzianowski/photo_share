from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
       Configuration settings for the application.

       Attributes:
           sqlalchemy_database_url (str): The URL for the SQLAlchemy database.
           secret_key (str): The secret key for the application.
           algorithm (str): The algorithm used for authentication.
           mail_username (str): The username for the mail server.
           mail_password (str): The password for the mail server.
           mail_port (int): The port for the mail server.
           mail_server (str): The address of the mail server.
           mail_from (str): The sender's email address.
           mail_starttls (bool): Flag indicating whether to use STARTTLS for mail.
           mail_ssl_tls (bool): Flag indicating whether to use SSL/TLS for mail.
           use_credentials (bool): Flag indicating whether to use credentials.
           validate_certs (bool): Flag indicating whether to validate certificates.
           redis_host (str): The hostname of the Redis server.
           redis_port (int): The port for the Redis server.
           redis_password (str): The Redis database password.
           cloudinary_name (str): The name of the Cloudinary account.
           cloudinary_api_key (str): The API key for Cloudinary.
           cloudinary_api_secret (str): The API secret for Cloudinary.

       Config:
           env_file (str): The path to the environment file.
           env_file_encoding (str): The encoding of the environment file.
       """
    sqlalchemy_database_url: str

    secret_key: str
    algorithm: str

    mail_username: str
    mail_password: str
    mail_port: int
    mail_server: str
    mail_from: str
    mail_starttls: bool
    mail_ssl_tls: bool
    use_credentials: bool
    validate_certs: bool

    redis_host: str
    redis_port: int
    redis_password: str

    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()