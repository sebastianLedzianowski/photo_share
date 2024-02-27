from sqlalchemy import Column, Integer, String, func
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql.sqltypes import DateTime, Boolean

Base = declarative_base()

class User(Base):
    """
    SQLAlchemy model representing a user.

    Attributes:
        id (int): Primary key for the user.
        username (str): Username of the user.
        email (str): Email address of the user (unique).
        password (str): Password of the user.
        created_at (DateTime): Timestamp indicating when the user was created.
        avatar (str): Filepath to the user's avatar (nullable).
        refresh_token (str): Refresh token for the user (nullable).
        confirmed (bool): Flag indicating whether the user is confirmed.
        admin (bool): Flag indicating whether the user has admin privileges.
        moderator (bool): Flag indicating whether the user has moderator permissions.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column('crated_at', DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    admin = Column(Boolean, default=False)
    moderator = Column(Boolean, default=False)

    def dict(self):
        """
        Convert user data to a dictionary.

        Returns:
            dict: User data as a dictionary.
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "created_at": self.created_at,
            "avatar": self.avatar,
            "refresh_token": self.refresh_token,
            "confirmed": self.confirmed,
            "admin": self.admin,
            "moderator": self.moderator
        }