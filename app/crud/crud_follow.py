from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.follow import Follow

def get_follow(db: Session, follower_id: str, following_id: str) -> Follow | None:
    return db.scalar(select(Follow).where(Follow.follower_id == follower_id, Follow.following_id == following_id))

def create_follow(db: Session, follower_id: str, following_id: str) -> Follow:
    new_follow = Follow(follower_id=follower_id, following_id=following_id)
    db.add(new_follow)
    db.commit()
    db.refresh(new_follow)
    return new_follow

def delete_follow(db: Session, db_follow: Follow):
    db.delete(db_follow)
    db.commit()

def get_followers(db: Session, user_id: str):
    return db.scalars(select(Follow).where(Follow.following_id == user_id)).all()

def get_following(db: Session, user_id: str):
    return db.scalars(select(Follow).where(Follow.follower_id == user_id)).all()