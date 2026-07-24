import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database.database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"
    #UUID:Benzersiz 128 bitlik bir sayıdır
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)

    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    bio = Column(Text, nullable=True)
    profile_image_url= Column(String, nullable=True)

    #soft delete:kullanıcıyı silmek yerine pasife alma
    is_active = Column(Boolean, default=True)

    #zaman damgaları ---> db sunucusunun saatini baz alır
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Bir kullanıcı silindiğinde (cascade="all, delete-orphan"), onun yazdığı tüm yazılar da otomatik silinir
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")