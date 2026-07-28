from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.like import Like

def get_like(db: Session, post_id: str, user_id: str) -> Like | None:
    return db.scalar(select(Like).where(Like.post_id == post_id, Like.user_id == user_id))

def get_likes_by_post(db: Session, post_id: str):
    return db.scalars(select(Like).where(Like.post_id == post_id)).all()

def create_like(db: Session, post_id: str, user_id: str) -> Like:
    new_like = Like(post_id=post_id, user_id=user_id)
    db.add(new_like)
    db.commit()
    db.refresh(new_like)
    return new_like

def delete_like(db: Session, db_like: Like):
    db.delete(db_like)
    db.commit()