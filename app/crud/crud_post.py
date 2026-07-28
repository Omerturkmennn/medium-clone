from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.post import Post
from app.models.follow import Follow
from app.schemas.post import PostCreate, PostUpdate

def get_post_by_id(db: Session, post_id: str) -> Post | None:
    """ID'ye göre veritabanından tek bir makale getirir."""
    return db.scalar(select(Post).where(Post.id == post_id))

def get_posts(db: Session):
    """Tüm makaleleri veritabanından çeker."""
    return db.scalars(select(Post)).all()

def create_post(db: Session, post_in: PostCreate, author_id: str) -> Post:
    """Yeni makaleyi veritabanına kaydeder."""
    new_post = Post(
        title=post_in.title,
        content=post_in.content,
        author_id=author_id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

def update_post(db: Session, db_post: Post, post_in: PostUpdate) -> Post:
    """Mevcut bir makalenin başlık veya içeriğini günceller."""
    if post_in.title is not None:
        db_post.title = post_in.title
    if post_in.content is not None:
        db_post.content = post_in.content

    db.commit()
    db.refresh(db_post)
    return db_post

def delete_post(db: Session, db_post: Post):
    """Makaleyi veritabanından kalıcı olarak siler."""
    db.delete(db_post)
    db.commit()

def get_feed_posts(db: Session, user_id: str):
    """Kullanıcının sadece takip ettiği kişilerin makalelerini getirir."""
    following_ids = db.scalars(
        select(Follow.following_id).where(Follow.follower_id == user_id)
    ).all()

    if not following_ids:
        return []

    return db.scalars(
        select(Post)
        .where(Post.author_id.in_(following_ids))
        .order_by(Post.created_at.desc())
    ).all()