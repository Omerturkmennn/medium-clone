from sqlalchemy import Column, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone

from app.database.database import Base

class Like(Base):
    __tablename__ = "likes"
    id=Column(String, primary_key=True, index=True,default=lambda:str(uuid.uuid4()))

    # Hangi kullanıcı beğendi
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    #Hangi makaleyi beğendi
    post_id = Column(String, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)

    #Ne zaman beğenildi?
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    #Bir kullanıcı (user_id) bir makaleyi (post_id) yalnızca bir kez beğenebilir
    #Eğer aynı kişi aynı makaleye ikinci bir beğeni atmaya kalkarsa veritabanı hata fırlatır--->UniqueConstraint
    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uix_user_post_like"),
    )

    #İlişkiler
    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")