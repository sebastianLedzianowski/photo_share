from sqlalchemy.orm import Session

from src.database.models import Rating, User

async def add_rating_to_picture(picture_id: int, rating: int, user: User, db: Session):
    """
    Adds or updates a rating for a picture by a specific user.

    Parameters:
        picture_id (int): The ID of the picture to rate.
        rating (int): The rating value.
        user (User): The user giving the rating.
        db (Session): Database session object.

    Returns:
        dict: A message indicating that the rating was successfully created or updated.
    """
    rating_record = db.query(Rating).filter(Rating.picture_id == picture_id).first()
    if not rating_record:
        new_rating = Rating(picture_id=picture_id, data={str(rating): [user.id]})
        db.add(new_rating)

    else:
        rating_data = rating_record.data
        for rat, users in rating_data.items():
            if user.id in users:
                users.remove(user.id)
        rating_data[str(rating)] = rating_data.get(str(rating), []) + [user.id]
        rating_record.data = rating_data
    db.commit()
    return {"message": "The rating was successfully created or updated."}


async def remove_rating_from_picture(picture_id: int, user: User, db: Session):
    """
        Removes a rating from a picture by a specific user.

        Parameters:
            picture_id (int): The ID of the picture from which to remove the rating.
            user (User): The user whose rating is to be removed.
            db (Session): Database session object.

        Returns:
            dict: A message indicating the outcome of the operation.
        """
    rating_record = db.query(Rating).filter(Rating.picture_id == picture_id).first()
    if not rating_record:
        return {"message": "No rating for picture."}

    else:
        rating_data = rating_record.data
        rating_data_copy = rating_data.copy()
        for rat, users in rating_data_copy.items():
            if user.id in users:
                users.remove(user.id)
                if not users:
                    del rating_data[rat]
        if rating_data:
            rating_record.data = rating_data
        else:
            db.delete(rating_record)
        db.commit()
        return {"message": "Rating removed successfully." if rating_data else "No ratings left, rating record deleted."}

async def get_rating(picture_id: int, db: Session):
    """
    Retrieves all ratings for a specific picture.

    Parameters:
        picture_id (int): The ID of the picture whose ratings are to be retrieved.
        db (Session): Database session object.

    Returns:
        dict: A dictionary containing usernames as keys and their respective ratings as values.
    """
    rating_record = db.query(Rating).filter(Rating.picture_id == picture_id).first()
    if not rating_record:
        return {"message": "No rating for picture."}

    rating_data = rating_record.data
    ratings = {}
    for rat, users_ids in rating_data.items():
        for user_id in users_ids:
            user = db.query(User).filter(User.id == user_id).first()
            ratings[user.username] = rat
    return ratings


async def get_average_of_rating(picture_id: int, db: Session):
    """
    Calculates the average rating for a specific picture.

    Parameters:
        picture_id (int): The ID of the picture whose average rating is to be calculated.
        db (Session): Database session object.

    Returns:
        dict: A message containing the average rating if available, otherwise indicating no ratings.
    """
    rating_record = db.query(Rating).filter(Rating.picture_id == picture_id).first()
    if not rating_record:
        return {"message": "No rating for picture"}

    rating_data = rating_record.data
    total_sum = 0
    total_count = 0

    for rat, users in rating_data.items():
        rat_value = int(rat)
        count = len(users)
        total_sum += rat_value * count
        total_count += count

    if total_count == 0:
        return {"message": "No ratings to calculate average."}

    average_rating = total_sum / total_count
    return {"average_rating": average_rating}