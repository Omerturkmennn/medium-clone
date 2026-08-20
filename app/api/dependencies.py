from typing import Generator

from aiohttp import payload
from fastapi import Depends, HTTPException, status,Query,WebSocketException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select
import jwt

from app.database.database import SessionLocal
from app.core.config import settings
from app.models.user import User


# Bu sınıf, gelen isteklerin Authorization başlığına bakar ve
# "Bearer <token_metni>" formatında bir token olup olmadığını kontrol eder.
# Eğer token yoksa, FastAPI otomatik olarak 403 (Forbidden) hatası döndürür.
security = HTTPBearer()


def get_db() -> Generator:
    """
    Bu fonksiyon her API isteğinde veritabanı ile yeni bir bağlantı (oturum) açar.
    İstek başarılı veya hatalı tamamlansa bile 'finally' bloğu sayesinde
    veritabanı bağlantısı güvenli bir şekilde kapatılır.
    Böylece veritabanı şişmez ve performans düşmez.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
        # Depends(security) sayesinde bu fonksiyon her çalıştığında önce HTTPBearer çalışır
        # ve geçerli bir token formatı yakalayıp 'credentials' değişkenine atar.
        credentials: HTTPAuthorizationCredentials = Depends(security),
        # Aynı anda veritabanı bağlantısını da çağırıyoruz ki kullanıcıyı sorgulayabilelim.
        db: Session = Depends(get_db)
) -> User:
    """
    Gelen JWT token'ı çözen ve token içindeki ID'ye sahip kullanıcıyı
    veritabanından bularak geri döndüren ana güvenlik fonksiyonumuz.
    Bunu korumak istediğimiz her endpoint'te kullanacağız.
    """

    # HTTPBearer bize Bearer token_metni içindeki sadece token_metni kısmını verir
    token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        # Token oluştururken kullanıcının ID'sini "sub" (subject) anahtarına koyacağız.
        # Şimdi o ID'yi geri okuyoruz.
        user_id: str = payload.get("sub")
        # Tokenın tipini payloaddan al
        token_type: str = payload.get("type")

        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Token içinde kullanıcı bilgisi bulunamadı")

        if token_type != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Geçersiz token tipi. Lütfen access token kullanın.")

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Token kullanım süresi dolmuş,tekrar giriş yapınız")

    #token geçersiz ise
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Geçersiz token")

    # Eğer buraya kadar geldiyse token sağlam demektir
    # Şimdi bu ID ye sahip kullanıcı gerçekten veritabanımızda var mı diye bakıyoruz
    user: User | None = db.scalar(select(User).where(User.id == user_id))

    #Kullanıcı silinmişse ama elinde eski bir token varsa onu da engelliyoruz.
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bu token'a ait kullanıcı veritabanında bulunamadı."
        )

    # Tüm kontrollerden başarıyla geçti, kullanıcı nesnesini endpoint'e gönderiyoruz.
    return user

#WebSocket isteklerinde tokenı Query parametresinden alıp doğrulamak için özel fonksiyon
def get_current_user_ws(
        token:str=Query(...),
        db: Session = Depends(get_db)
)->User:
    try:
        #tokeni çöz
        payload=jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        #eğer geçersiz ise ws kapatma hatası yolla
        if user_id is None or token_type != "access":
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    # ExpiredSignatureError veya InvalidTokenError durumunda
    except jwt.PyJWTError:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    #db de kullanıcı var mı kontrol
    user=db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    return user

