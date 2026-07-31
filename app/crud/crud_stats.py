from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.post import Post
from app.models.like import Like

def get_user_statistics(db: Session, user_id:str):
    """Kullanıcının toplam makale, okunma, beğeni sayılarını ve trend makalelerini hesaplar."""

    #toplam yayınlanmış makale sayısı
    total_articles=db.scalar(
        select(func.count(Post.id))
        .where(Post.author_id == user_id, Post.status == "published")

    )or 0

    #toplam okunma sayısı
    total_views=db.scalar(
        select(func.sum(Post.view_count))
        .where(Post.author_id == user_id, Post.status == "published")
    ) or 0

    #toplam beğeni sayısı
    total_likes=db.scalar(
        select(func.count(Like.id))
        .join(Post, Like.post_id == Post.id)
        .where(Post.author_id == user_id, Post.status == "published")
    ) or 0

    #trend olan makaleler
    #en cok okunan 3 makalesi
    trending_posts=db.scalars(
        select(Post)
        .where(Post.author_id == user_id, Post.status == "published")
        .order_by(Post.view_count.desc())
        .limit(3)
    ).all()

    return {
        "total_articles": total_articles,
        "total_views": total_views,
        "total_likes": total_likes,
        "trending_posts": trending_posts
    }