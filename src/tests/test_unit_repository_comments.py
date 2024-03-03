from datetime import datetime

import pytest
from sqlalchemy.orm import Session
from src.repository import comments
from src.database.models import Comment
from unittest.mock import patch


@pytest.mark.asyncio
async def test_add_new_comment_to_db_success(session: Session):
    comment = Comment(user_id=1, picture_id=1, content="Test comment", created_at=datetime.now(), update_at=datetime.now())
    result = await tags.add_new_tags_to_db(session, tags_to_add)

    # Assert
    assert len(new_tags) == len(tags_to_add)
    for tag in new_tags:
        assert isinstance(tag, Tag)
        assert tag.name in tags_to_add

@pytest.mark.asyncio
async def test_add_new_tags_to_db_with_existing_tags(session: Session):
    # Arrange
    existing_tags = ["tag1", "tag2"]
    tags_to_add = existing_tags + ["tag3", "tag4", "tag5"]
    mock_return_value = [Tag(name=tag) for tag in existing_tags]

    with patch('src.repository.tags.filter_existing_tags') as mock_filter_existing_tags:
        mock_filter_existing_tags.return_value = mock_return_value

        # Act
        new_tags = await tags.add_new_tags_to_db(session, tags_to_add)

    # Assert
    assert len(new_tags) == 3
    for tag in new_tags:
        assert isinstance(tag, Tag)
        assert tag.name in tags_to_add

@pytest.mark.asyncio
async def test_add_new_tags_to_db_with_existing_tags_only(session: Session):
    # Arrange
    existing_tags = ["tag1", "tag2", "tag3", "tag4", "tag5"]

    with patch('src.repository.tags.filter_existing_tags') as mock_filter_existing_tags:
        mock_filter_existing_tags.return_value = [Tag(name=tag) for tag in existing_tags]

        # Act
        new_tags = await tags.add_new_tags_to_db(session, existing_tags)

    # Assert
    assert len(new_tags) == 0

@pytest.mark.asyncio
async def test_add_new_tags_to_db_exceed_max_limit(session: Session):
    # Arrange
    tags_to_add = ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6"]

    with patch('src.repository.tags.filter_existing_tags') as mock_filter_existing_tags:
        mock_filter_existing_tags.return_value = []

        # Act / Assert
        with pytest.raises(ValueError):
            await tags.add_new_tags_to_db(session, tags_to_add)

@pytest.mark.asyncio
async def test_add_new_tags_to_db_invalid_input(session: Session):
    # Arrange
    invalid_inputs = [
        "tag1",  # string
        123,     # int
        {"tag": "tag1"},  # dict
        None,    # None
        [1, 2, 3],  # list of integers
        [1.0, 2.0, 3.0],  # list of floats
        [[], [], []],  # list of lists
        [True, False],  # list of booleans
        [(1, 2), (3, 4)],  # list of tuples
    ]

    # Act / Assert
    for invalid_input in invalid_inputs:
        with pytest.raises(TypeError):
            await tags.add_new_tags_to_db(session, invalid_input)