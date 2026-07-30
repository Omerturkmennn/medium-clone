from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.bookmark import Bookmark

def get_bookmark(db:Session,user_id:str,post_id:str) -> Bookmark:
    """Kullanıcının belirli bir makaleyi daha önce kaydedip kaydetmediğini kontrol eder."""
    return db.scalar(select(Bookmark).where(Bookmark.user_id == user_id, Bookmark.post_id == post_id))

def create_bookmark(db:Session,user_id:str,post_id:str) -> Bookmark:
    """Makaleyi okuma listesine ekler"""
    new_bookmark = Bookmark(user_id=user_id,post_id=post_id)
    db.add(new_bookmark)
    db.commit()
    db.refresh(new_bookmark)
    return new_bookmark

def delete_bookmark(db:Session,db_bookmark:Bookmark):
    """Makaleyi okuma listesinden çıkarır"""
    db.delete(db_bookmark)
    db.commit()

def get_user_bookmarks(db:Session,user_id:str):
    """Kullanıcının kaydettiği makaleleri listeler"""
    return db.scalars(select(Bookmark).where(Bookmark.user_id == user_id)).all()