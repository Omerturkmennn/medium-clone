import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database.database import Base

class Bookmark(Base):
    __tablename__ = "bookmarks"

    #her kaydetme için unique id
    id = Column(String, primary_key=True, default=lambda: uuid.uuid4().hex, index=True)

    #hangi kullanıcı kaydetti?  Kullanıcı silinirse kaydettiğide silinsin
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    #hangi makaleyi kaydetti
    post_id = Column(String, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)

    #ne zaman kaydetti
    created_at = Column(DateTime(timezone=True), server_default=func.now())