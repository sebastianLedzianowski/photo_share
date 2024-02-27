from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.secrets_manager import get_secret

SQLALCHEMY_DATABASE_URL = get_secret()

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Function to obtain a database session.

    Returns:
        sqlalchemy.orm.Session: A SQLAlchemy database session.

    Yields:
        sqlalchemy.orm.Session: A SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
