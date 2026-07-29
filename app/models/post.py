from sqlalchemy import Column, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
import uuid


# Veritabanı ana sınıfımız (alembic in tanıdığı Base)
from app.database.database import Base
from app.schemas.post import PostStatus



class Post(Base):
    __tablename__ = "posts"

    #her gönderinin id si olacak
    id = Column(String, primary_key=True, index=True,default=lambda: str(uuid.uuid4()))

    #yazı başlığı ve içeriği
    title = Column(String,nullable=False)
    content = Column(Text,nullable=False)

    #Foreign key-->yazının kime ait olduğunu tutan ID
    author_id = Column(String, ForeignKey("users.id",ondelete="CASCADE"), nullable=False)

    #yazının oluşşturulma ve güncelleme tarihleri
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),onupdate=func.now())

    #  yazıyı çekerken post.author.username diyerek
    # o yazıyı yazan kişinin bilgilerine kolayca ulaşabileceğiz.
    author = relationship("User", back_populates="posts")

    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

    # Makaleye gelen beğeniler 
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")

    #makale etiketlerini çekecek ilişki
    tags = relationship("Tag", secondary="post_tag", back_populates="posts")

    status=Column(String, nullable=False,default="draft")

    #URL'de görünecek olan slug sütunu. Hızlı arama için index=True, çakışmaması için unique=True yapıldı
    slug = Column(String, unique=True, index=True, nullable=True)

    #Makalenin kapak fotoğrafı yolu
    cover_image = Column(String, nullable=True)