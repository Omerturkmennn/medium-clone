from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from app.core.config import settings

REFRESH_TOKEN_EXPIRE_DAYS = 7

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kullanıcının girdiği düz şifre ile veritabanındaki hash'lenmiş şifreyi karşılaştırır."""

    password_bytes = plain_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')

    return bcrypt.checkpw(password_bytes, hash_bytes)

def get_password_hash(password: str) -> str:
    """Düz şifreyi geri döndürülemez bir hash'e (bcrypt) çevirir."""

    # Şifreyi bayt formatına çeviriyoruz
    password_bytes = password.encode('utf-8')

    # Güvenlik için rastgele bir 'tuz' (salt) üretiyoruz
    salt = bcrypt.gensalt()

    # Şifreyi hashliyoruz
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)

    # Veritabanına String olarak kaydedebilmek için tekrar metne (decode) çeviriyoruz
    return hashed_bytes.decode('utf-8')


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Kullanıcı giriş yaptığında ona verilecek olan JWT (kimlik kartı) üretir."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire,"type": "access"})

    # Token'ı gizli anahtarımızla (SECRET_KEY) imzalıyoruz
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta | None = None)->str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    #Token'ın içine bunun bir 'refresh' token olduğunu belirten bir etiket ekliyoruz
    to_encode.update({"exp": expire, "type": "refresh"})


    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt