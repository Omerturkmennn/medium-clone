import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.database.database import Base



#Bloklist:Çıkış yapan kullanıcının refresh token ını bu kara listeye ekleyeceğiz ve biri token yenilemek istediğinde
# önce bu listede var mı diye bakılacak

class TokenBlocklist(Base):
    """
    Çıkış (Logout) yapan kullanıcıların Refresh Token'larını
    tuttuğumuz Kara Liste tablosu.
    """
    __tablename__ = "token_blocklist"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)

    # İptal edilen token  burada saklanacak
    token = Column(String, unique=True, index=True, nullable=False)

    # Tokenın ne zaman kara listeye alındığı
    created_at = Column(DateTime(timezone=True), server_default=func.now())