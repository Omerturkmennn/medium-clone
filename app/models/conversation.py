import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base


class Conversation(Base):
    """İki kullanıcı arasındaki sohbet odasını temsil eder."""
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)

    # Sohbet eden iki kişinin ID
    user1_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user2_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Sohbet listesini en son atılan mesaja göre sıralamak için
    last_message_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # İlişkiler
    user1 = relationship("User", foreign_keys=[user1_id])
    user2 = relationship("User", foreign_keys=[user2_id])
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
