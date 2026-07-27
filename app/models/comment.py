from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone

from app.database.database import Base

class Comment(Base):
    __tablename__ = "comments"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    content = Column(Text, nullable=False)
    author_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    #Bu yorum hangi makaleye yapıldı (posts tablosundaki id ile eşleşir)
    post_id = Column(String, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)

    #Zaman damgaları
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    #ORM ilişkileri
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

