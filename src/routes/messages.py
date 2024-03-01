from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import MessageModel, MessageResponse, MessageSend
from src.database.db import get_db
from src.repository import messages as repository_messages
from src.services.auth import auth_service

router = APIRouter(prefix='/messages', tags=["messages"])


@router.post('/', response_model=MessageModel)
async def create_message(
        body: MessageSend,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
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
      injection system.

    Returns:
    - The created message as a MessageModel instance, including the newly assigned message ID.
    """
    message = await repository_messages.create_message(
        db=db,
        sender_id=current_user.id,
        receiver_id=body.receiver_id,
        content=body.content
    )
    if not message:
        raise HTTPException(status_code=400, detail="Message could not be created.")
    return message


@router.get('/user/{user_id}', response_model=List[MessageResponse])
async def get_messages_for_user(
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
) -> List[MessageResponse]:
    """
    Retrieve all messages sent by or to a specific user.

    This endpoint fetches and returns all messages where the specified user ID matches
    either the sender or the receiver. It is useful for displaying a user's message history.

    Parameters:
    - user_id (int): The ID of the user whose messages are to be retrieved. This is captured
      from the URL path.
    - db (Session, optional): An SQLAlchemy database session instance provided by the FastAPI dependency
      injection system.

    Returns:
    - A list of MessageResponse models representing all relevant messages. Each MessageResponse
      includes details such as the message ID, sender ID, receiver ID, content, and timestamp.
    """
    messages = await repository_messages.get_messages_for_user(user_id=current_user.id, db=db)
    return messages
