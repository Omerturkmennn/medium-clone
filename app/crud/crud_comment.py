from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate

def get_comment_by_id(db: Session, comment_id: str) -> Comment | None:
    return db.scalar(select(Comment).where(Comment.id == comment_id))

def get_comments_by_post(db: Session, post_id: str):
    return db.scalars(select(Comment).where(Comment.post_id == post_id)).all()

def create_comment(db: Session, comment_in: CommentCreate, post_id: str, author_id: str) -> Comment:
    new_comment = Comment(
        content=comment_in.content,
        post_id=post_id,
        author_id=author_id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

def update_comment(db: Session, db_comment: Comment, comment_in: CommentUpdate) -> Comment:
    if comment_in.content is not None:
        db_comment.content = comment_in.content
    db.commit()
    db.refresh(db_comment)
    return db_comment

def delete_comment(db: Session, db_comment: Comment):
    db.delete(db_comment)
    db.commit()