from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.tag import Tag

def get_all_tags(db: Session, limit: int = 20):
    """Veritabanındaki etiketleri listeler."""
    return db.scalars(
        select(Tag)
        .order_by(Tag.name)
        .limit(limit)
    ).all()
