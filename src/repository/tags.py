from typing import List
from sqlalchemy.orm import Session
from src.database.models import Tag

async def filter_existing_tags(db: Session, tags: List[str]) -> List[Tag]:
    """
    Filter existing tags from the database based on a list of tag names.

    This function queries the database to retrieve existing tags whose names match
    the provided list of tag names.

    Parameters:
    - db (Session): The SQLAlchemy session used to interact with the database.
    - tags (List[str]): A list of tag names to be filtered.

    Returns:
    - List[Tag]: A list of existing Tag objects retrieved from the database.
    """
    existing_tags = db.query(Tag).filter(Tag.name.in_(tags)).all()
    return existing_tags

async def add_new_tags_to_db(db: Session, tags: List[str]) -> List[Tag]:
    """
    Add new tags to the database.

    This function adds new tags to the database. If a tag with the same name already
    exists in the database, it is skipped.

    Parameters:
    - db (Session): The SQLAlchemy session used to interact with the database.
    - tags (Union[List[str], str]): A list of tag names to be added to the database. If a single tag
      is provided as a string, it will be converted to a list internally.

    Returns:
    - List[Tag]: A list of newly created Tag objects added to the database.
    
    Raises:
    - TypeError: If the provided tags are not in the correct format (list of strings).
    - ValueError: If the number of tags exceeds the maximum limit.
    """

    max_limit = 5
    if len(tags) > max_limit:
        raise ValueError(f"Number of tags exceeds the maximum limit of {max_limit}")
    elif not isinstance(tags, list):
        raise TypeError("Tags must be provided as a list of strings.")
    elif not all(isinstance(item, str) for item in tags):
        raise TypeError("Tags must be provided as a list of strings.")

    existing_tags = await filter_existing_tags(db, tags)
    tag_name_to_id = {tag.name: tag.id for tag in existing_tags}
    new_tags = [Tag(name=tag_name) for tag_name in tags if tag_name not in tag_name_to_id]
    db.add_all(new_tags)
    db.commit()

    for tag in new_tags:
        db.refresh(tag)

    return new_tags
