import uuid
from sqlalchemy import Column, String, Table, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base

#ARA TABLO (Association Table)
# Bu tablo sadece post_id ve tag_id'leri eşleştirir
# Kendi başına bir Model sınıfı olmasına gerek yoktur, SQLAlchemy'nin Table objesi yeterlidir
post_tag_association = Table(
    "post_tag", Base.metadata,
    Column("post_id", String, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", String, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

#Asıl etiket
class Tag(Base):
    __tablename__ = "tags"
    id = Column(String, primary_key=True,default=lambda: str(uuid.uuid4()))
    #her etiket unique olsun ki aynı etiketten 2 tane açılmasın
    name=Column(String,unique=True,nullable=False,index=True)

    # İLİŞKİ: Bu etiketin bağlı olduğu makaleleri bulmak için
    # secondary parametresi ile ara tablomuzu işaret ediyoruz
    posts = relationship("Post",secondary=post_tag_association, back_populates="tags")