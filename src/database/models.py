from sqlalchemy import Column, Integer, String, func, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql.sqltypes import DateTime, Boolean

Base = declarative_base()

class PictureTagsAssociation(Base):
    """
    SQLAlchemy model representing the association between pictures and tags.

    Attributes:
        picture_id (int): Foreign key referencing the id of the picture.
        tag_id (int): Foreign key referencing the id of the tag.
    """
    __tablename__ = 'picture_tags_association'

    picture_id = Column(Integer, ForeignKey('picture.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tag.id'), primary_key=True)

class Tag(Base):
    """
    SQLAlchemy model representing a tag.

    Attributes:
        id (int): Primary key for the tag.
        name (str): Name of the tag (unique).
    """
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    pictures = relationship('Picture', secondary='picture_tags_association', back_populates='tags')

class Picture(Base):
    """
    SQLAlchemy model representing a picture.

    Attributes:
        id (int): Primary key for the picture.
        user_id (int): Foreign key referencing the id of the user who uploaded the picture.
        rating (int): Rating of the picture (nullable).
        user (User): Relationship with the User model representing the uploader of the picture.
        tags (list[Tag]): Relationship with the Tag model representing tags associated with the picture.
        comments (list[Comment]): Relationship with the Comment model representing comments on the picture.
    """
    __tablename__ = "picture"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    rating = Column(Integer, nullable=True)

    user = relationship('User', back_populates='pictures')
    tags = relationship('Tag', secondary='picture_tags_association', back_populates='pictures')
    comments = relationship('Comment', back_populates='picture')

class Comment(Base):
    """
    SQLAlchemy model representing a comment.

    Attributes:
        id (int): Primary key for the comment.
        user_id (int): Foreign key referencing the id of the user who posted the comment.
        picture_id (int): Foreign key referencing the id of the picture associated with the comment.
        content (str): Content of the comment.
        likes (list[CommentLike]): Relationship with the CommentLike model representing likes on the comment.
        picture (Picture): Relationship with the Picture model representing the associated picture.
        user (User): Relationship with the User model representing the user who posted the comment.
    """
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    picture_id = Column(Integer, ForeignKey('picture.id'))
    content = Column(String(255), nullable=False)

    likes = relationship('CommentLike', back_populates='comment')
    picture = relationship('Picture', back_populates='comments')
    user = relationship('User', back_populates='comments')

class CommentLike(Base):
    """
    SQLAlchemy model representing a like on a comment.

    Attributes:
        id (int): Primary key for the like.
        user_id (int): Foreign key referencing the id of the user who liked the comment.
        comment_id (int): Foreign key referencing the id of the liked comment.
        user (User): Relationship with the User model representing the user who liked the comment.
        comment (Comment): Relationship with the Comment model representing the liked comment.
    """
    __tablename__ = "comment_like"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    comment_id = Column(Integer, ForeignKey('comment.id'))

    user = relationship('User', back_populates='comment_likes')
    comment = relationship('Comment', back_populates='likes')

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
        pictures (list[Picture]): Relationship with the Picture model representing pictures uploaded by the user.
        comments (list[Comment]): Relationship with the Comment model representing comments posted by the user.
        comment_likes (list[CommentLike]): Relationship with the CommentLike model representing likes given by the user.
        sent_messages (list[Message]): Relationship with the Message model representing messages sent by the user.
        received_messages (list[Message]): Relationship with the Message model representing messages received by the user.
    """
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column('crated_at', DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    admin = Column(Boolean, default=False)
    moderator = Column(Boolean, default=False)

    pictures = relationship('Picture', back_populates='user')
    comments = relationship('Comment', back_populates='user')
    comment_likes = relationship('CommentLike', back_populates='user')
    sent_messages = relationship('Message', back_populates='sender', foreign_keys='Message.sender_id')
    received_messages = relationship('Message', back_populates='receiver', foreign_keys='Message.receiver_id')

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
class Message(Base):
    """
    SQLAlchemy model representing a message.

    Attributes:
        id (int): Primary key for the message.
        sender_id (int): Foreign key referencing the id of the user who sent the message.
        receiver_id (int): Foreign key referencing the id of the user who received the message.
        content (str): Content of the message.
        timestamp (DateTime): Timestamp indicating when the message was sent.
        sender (User): Relationship with the User model representing the sender of the message.
        receiver (User): Relationship with the User model representing the receiver of the message.
    """
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey('user.id'))
    receiver_id = Column(Integer, ForeignKey('user.id'))
    content = Column(String(255), nullable=False)
    timestamp = Column('timestamp', DateTime, default=func.now())

    sender = relationship('User', back_populates='sent_messages', foreign_keys=[sender_id])
    receiver = relationship('User', back_populates='received_messages', foreign_keys=[receiver_id])