import pytest
from sqlalchemy.orm import Session
from src.repository import tags
from src.database.models import Tag
from unittest.mock import patch

@pytest.mark.asyncio
async def test_add_new_tags_to_db_with_new_tags_only(session: Session):
    new_tags = ["tag1", "tag2", "tag3", "tag4", "tag5"]
       
    mock_return_value = []
    
    with patch.object(session.query(Tag), 'filter', return_value=mock_return_value):
        response = await tags.add_tags_to_db(picture_id=1, tags=new_tags, db=session)

    assert len(response.new_tags) == len(new_tags)
    for tag_model, new_tag in zip(response.new_tags, new_tags):
        assert tag_model.name == new_tag
    
    assert len(response.existing_tags) == 0


@pytest.mark.asyncio
async def test_add_new_tags_to_db_with_existing_tags(session: Session):
    existing_tags = ["tag1", "tag2"]
    new_tags = ["tag3", "tag4", "tag5"]
    
    session.add_all([Tag(name=name) for name in existing_tags])
    session.commit()
    
    all_tags = existing_tags + new_tags

    mock_return_value = [Tag(name=name) for name in existing_tags]

    with patch.object(session.query().filter(), 'all', return_value=mock_return_value):
        response = await tags.add_tags_to_db(picture_id=1, tags=all_tags, db=session)

    assert len(response.new_tags) == len(new_tags)
    for tag_model, new_tag in zip(response.new_tags, new_tags):
        assert tag_model.name == new_tag
    
    assert len(response.existing_tags) == len(existing_tags)
    for tag_model, existing_tags in zip(response.existing_tags, existing_tags):
        assert tag_model.name == existing_tags


@pytest.mark.asyncio
async def test_add_new_tags_to_db_with_existing_tags_only(session: Session):
    existing_tags = ["tag1", "tag2", "tag3", "tag4", "tag5"]
    
    session.add_all([Tag(name=name) for name in existing_tags])
    session.commit()

    all_tags = existing_tags

    mock_return_value = [Tag(name=name) for name in existing_tags]

    with patch.object(session.query().filter(), 'all', return_value=mock_return_value):
        response = await tags.add_tags_to_db(picture_id=1, tags=all_tags, db=session)

    assert len(response.new_tags) == 0
    
    assert len(response.existing_tags) == len(existing_tags)
    for tag_model, existing_tag in zip(response.existing_tags, existing_tags):
        assert tag_model.name == existing_tag


@pytest.mark.asyncio
async def test_add_new_tags_to_db_exceed_max_limit(session: Session):
    tags_to_add = ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6"]

    with pytest.raises(ValueError):
        await tags.add_tags_to_db(picture_id=1, tags=tags_to_add, db=session)


@pytest.mark.asyncio
async def test_add_new_tags_to_db_invalid_input(session: Session):
    invalid_inputs_tags = [
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

    invalid_inputs_picture_id = [
        "tag1",  # string
        {"tag": "tag1"},  # dict
        None,    # None
        ["kotek","piesek"],  # list of strings
        [1, 2, 3],  # list of integers
        [1.0, 2.0, 3.0],  # list of floats
        [[], [], []],  # list of lists
        [True, False],  # list of booleans
        [(1, 2), (3, 4)],  # list of tuples
    ]

    for invalid_input in invalid_inputs_tags:
        with pytest.raises(TypeError):
            await tags.add_tags_to_db(picture_id=1, tags=invalid_input, db=session)

    for invalid_input in invalid_inputs_picture_id:
        with pytest.raises(TypeError):
            await tags.add_tags_to_db(picture_id=invalid_input, tags=["kotek"], db=session)
