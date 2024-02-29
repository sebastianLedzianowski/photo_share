from typing import List

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from src.schemas import MessageModel, MessageResponse
from src.database.db import get_db
from src.repository import messages as repository_messages


router = APIRouter(prefix='/messages', tags=["messages"])


@router.post('/', response_model=MessageModel)
async def create_message(
        body: MessageModel,
        db: Session = Depends(get_db)
):
    """
    Create a new message in the database.

    This endpoint accepts a JSON payload representing a message, including the sender's ID,
    the receiver's ID, and the message content. It creates a new message record in the database
    and returns the created message data, including its database-assigned ID.

    Parameters:
    - body (MessageModel): A Pydantic model that includes the sender_id, receiver_id, and content
      of the message. This is parsed from the request body.
    - db (Session, optional): An SQLAlchemy database session instance provided by the FastAPI dependency
      injection system. Defaults to Depends(get_db).

    Returns:
    - The created message as a MessageModel instance, including the newly assigned message ID.
    """
    return await repository_messages.create_message(body=body, db=db)


@router.get('/user/{user_id}', response_model=List[MessageResponse])
async def get_messages_for_user(
        user_id: int,
        db: Session = Depends(get_db)
) -> List[MessageResponse]:
    """
    Retrieve all messages sent by or to a specific user.

    This endpoint fetches and returns all messages where the specified user ID matches
    either the sender or the receiver. It is useful for displaying a user's message history.

    Parameters:
    - user_id (int): The ID of the user whose messages are to be retrieved. This is captured
      from the URL path.
    - db (Session, optional): An SQLAlchemy database session instance provided by the FastAPI dependency
      injection system. Defaults to Depends(get_db).

    Returns:
    - A list of MessageResponse models representing all relevant messages. Each MessageResponse
      includes details such as the message ID, sender ID, receiver ID, content, and timestamp.
    """
    messages = await repository_messages.get_messages_for_user(user_id=user_id, db=db)
    return messages
