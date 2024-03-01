from typing import List

from sqlalchemy.orm import Session
from src.database.models import Message
from src.schemas import MessageResponse


async def create_message(
        sender_id: int,
        receiver_id: int,
        content: str,
        db: Session
) -> Message:
    """
    Asynchronously creates a new message in the database.

    This function takes a message body and a database session, constructs a new
    Message object, and stores it in the database. It then refreshes the session
    to retrieve the newly created message with its database-generated ID and other
    default values filled in.

    Parameters:
    - body (MessageModel): A Pydantic model representing the message to be created,
      including the sender_id, receiver_id, and content of the message.
    - db (Session): The SQLAlchemy session used to interact with the database.

    Returns:
    - Message: The newly created Message object, refreshed from the database.
    """
    db_message = Message(sender_id=sender_id,
                         receiver_id=receiver_id,
                         content=content)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


async def get_messages_for_user(
        user_id: int,
        db: Session
) -> List[MessageResponse]:
    """
    Asynchronously retrieves all messages sent by or to a specific user from the database.

    This function queries the database for all messages where the given user_id matches
    either the sender_id or the receiver_id, effectively fetching all messages associated
    with the user.

    Parameters:
    - user_id (int): The ID of the user for whom to retrieve messages.
    - db (Session): The SQLAlchemy session used to interact with the database.

    Returns:
    - List[MessageResponse]: A list of MessageResponse models representing all messages
      found that were sent by or to the specified user. Each MessageResponse includes
      the message details such as sender_id, receiver_id, content, and timestamp.
    """
    messages = db.query(Message).filter(
        (Message.sender_id == user_id) | (Message.receiver_id == user_id)
    ).all()
    return messages
