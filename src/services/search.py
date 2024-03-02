from sqlalchemy import or_
from src.database.models import Base, Tag, User, Comment, Picture, PictureTagsAssociation
from typing import List


#Mother Function
def search(query: str, model: Base, fields: List[str]) -> List[Base]: # type: ignore
    """
    Searches for records in the given model that match the provided query string.

    Args:
        query (str): The query string to search for.
        model (Base): The SQLAlchemy model to search in.
        fields (Tuple[str, ...]): The fields of the model to search in.

    Returns:
        List[model]: A list of records that match the search criteria.
    """
    query_parts = query.split()
    query = model.query
    for query_part in query_parts:
        query = query.filter(or_(*[getattr(model, field).contains(query_part) for field in fields]))
    return query.all()


def search_pictures(keywords_or_tags: List[str]) -> List[Picture]:
    """
    Searches for pictures that match the given keywords or tags.

    Args:
        keywords_or_tags (List[str]): A list of keywords or tags to search for.

    Returns:
        List[Picture]: A list of pictures that match the search criteria.
    """
    return search(query=' '.join(keywords_or_tags), model=Picture, fields=('tags.name', 'description'))
    

def search_users(keywords: List[str]) -> List[User]:
    """
    Searches for users that match the given keywords.

    Args:
        keywords (List[str]): A list of keywords to search for.

    Returns:
        List[User]: A list of users that match the search criteria.
    """
    return search(query=' '.join(keywords), model=User, fields=('username', 'email'))


def search_users_with_photos(query: str = '', picture_ids: List[int] = None) -> List[User]:
    """
    Searches for users that match the given query and have added photos.

    Args:
        query (str, optional): The query string to search for in usernames.
        picture_ids (List[int], optional): A list of picture IDs to filter by.

    Returns:
        List[User]: A list of users that match the search criteria and have added photos.
    """
    query_params = {'username': query} if query else {}
    users = search_users(**query_params)

    if picture_ids:
        pictures = search_pictures(ids=picture_ids)
        user_ids = {picture.user_id for picture in pictures}
        users = [user for user in users if user.id in user_ids]

    return [user for user in users if user.pictures.count() > 0]


def search_comments(keywords_or_tags: List[str]) -> List[Comment]:
    """
    Searches for comments that match the given keywords or Tags.

    Args:
        keywords (List[str]): A list of keywords to search for.

    Returns:
        List[Comment]: A list of comments that match the search criteria.
    """
    tags = Tag.query.filter(Tag.name.in_(tags)).all()
    comments = Comment.query.join(Picture).join(PictureTagsAssociation).join(Tag).filter(Tag.id.in_([tag.id for tag in tags])).all()
    return comments

