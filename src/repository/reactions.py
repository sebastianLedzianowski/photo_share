from collections import Counter, OrderedDict

from sqlalchemy.orm import Session

from src.database.models import Reaction, User


async def add_reaction_to_comment(comment_id: int, reaction: str, user: User, db: Session):
    reaction_record = db.query(Reaction).filter(Reaction.comment_id == comment_id).first()
    if not reaction_record:
        new_reaction = Reaction(comment_id=comment_id, data={reaction: [user.id]})
        db.add(new_reaction)
    else:
        reaction_data = reaction_record.data
        reaction_data_copy = reaction_data.copy()
        for react, users in reaction_data_copy.items():
            if user.id in users:
                users.remove(user.id)
            if not users:
                del reaction_data[react]
        if reaction not in reaction_data:
            reaction_data[reaction] = [user.id]
        else:
            reaction_data[reaction].append(user.id)
        db.query(Reaction).filter(Reaction.comment_id == comment_id).update({"data": reaction_data})
    db.commit()
    return {"message": f"The reaction was created"}


async def remove_reaction_from_comment(comment_id: int, user: User, db: Session):
    reaction_record = db.query(Reaction).filter(Reaction.comment_id == comment_id).first()
    if not reaction_record:
        return {"message": "No reaction for comment"}
    else:
        reaction_data = reaction_record.data
        reaction_data_copy = reaction_data.copy()
        for react, users in reaction_data_copy.items():
            if user.id in users:
                users.remove(user.id)
            if not users:
                del reaction_data[react]
            if reaction_data:
                db.query(Reaction).filter(Reaction.comment_id == comment_id).update({"data": reaction_data})
            else:
                db.delete(reaction_record)
        db.commit()


async def get_reactions(comment_id: int, db: Session):
    reaction_record = db.query(Reaction).filter(Reaction.comment_id == comment_id).first()
    if not reaction_record:
        return {"message": "No reaction for comment"}
    reaction_data = reaction_record.data
    reactions = {}
    for react, users in reaction_data.items():
        for user_id in users:
            user = db.query(User).filter(User.id == user_id).first()
            reactions[user.username] = react
    return reactions


async def get_number_of_reactions(comment_id: int, db: Session):
    reaction_record = db.query(Reaction).filter(Reaction.comment_id == comment_id).first()
    if not reaction_record:
        return {"message": "No reaction for comment"}
    reaction_data = reaction_record.data
    number_of_reactions = Counter()
    for react, users in reaction_data.items():
        number_of_reactions[react] = len(users)
    return OrderedDict(number_of_reactions.most_common())

