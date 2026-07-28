from sqlalchemy import Column, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone

from app.database.database import Base

class Follow(Base):
    __tablename__ = "follow"

    id=Column(String, primary_key=True, index=True,default=lambda: str(uuid.uuid4()))

    #Takip eden kişi
    follower_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    #Takip edilen kişi
    following_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    #ne zaman takip etmeye başladı
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    #Bir kişi aynı kişiyi 2 kez takip edemez
    __table_args__ = (
        UniqueConstraint("follower_id", "following_id", name="uix_follower_following"),
    )

    # İLİŞKİLER:Her iki bağlantı da User tablosuna gittiği için foreign_keys belirterek Alchemy e yol gösteriliyor
    follower_user = relationship("User", foreign_keys=[follower_id], back_populates="following")
    following_user = relationship("User", foreign_keys=[following_id], back_populates="followers")