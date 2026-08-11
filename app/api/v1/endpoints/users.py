import credentials
from fastapi import APIRouter, Depends, HTTPException, status,Request,Body
from sqlalchemy.orm import Session
from app.schemas.stats import UserStatsResponse
from app.crud import crud_stats, crud_user
from sqlalchemy import select
from pydantic import BaseModel
import jwt
from app.core import security

# Yazdığımız veritabanı bağlantısı ve güvenlik fonksiyonlarını içeri alıyoruz
from app.api.dependencies import get_db,get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse,UserUpdate
from app.core.security import get_password_hash, verify_password, create_access_token
from app.crud import crud_user
from app.core.rate_limit import limiter

#Bu router ileride main.py içine eklenecek ve bu dosyadaki tüm endpointleri yönetecek
router = APIRouter()

# Sadece login işleminde dışarıdan e-posta ve şifre almak için
# kullandığımız tek kullanımlık, basit bir Pydantic veri doğrulama şeması.
class UserLogin(BaseModel):
    email: str
    password: str

# Kayıt olma endpointi
# response_model=UserResponse ile dışarıya şifreyi değil sadece profil bilgilerini dönüyoruz
@router.post("/register",response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")   # Bu IP den dakikada en fazla 5 kayıt isteği gelebilir
def register(request:Request,user_in:UserCreate, db: Session = Depends(get_db)):
    """
        Yeni bir kullanıcı oluşturur.
        Girilen e-posta veya kullanıcı adı sistemde varsa hata döndürür.
        Şifreyi güvenli bir şekilde hash'leyerek veritabanına kaydeder.
        """
    #e-posta sistemde kayıtlı mı diye kontrol
    user_by_email=crud_user.get_user_by_email(db, email=user_in.email)
    if user_by_email:
        raise HTTPException(status_code=400,detail="Bu E-posta zaten kullanılıyor")

    #username sisteme kayıtlı mı kontrolü
    user_by_username=crud_user.get_user_by_username(db, username=user_in.username)
    if user_by_username:
        raise HTTPException(status_code=400,detail="Bu kullanıcı adı zaten alınmış")

    #kullanıcının girdiği şifreyi hashle
    #db ye eklenecek kullanıcı nesnesi
    # ID, created_at gibi otomatik oluşan verileri nesneye geri yükle
    new_user = crud_user.create_user(db=db, user_in=user_in)

    return new_user

@router.post("/login")
@limiter.limit("10/minute") #bu IP den dakikada en fazla 10 istek gelebilir
def login_user(request:Request,user_in: UserLogin, db: Session = Depends(get_db)):
    """
        Kullanıcının e-posta ve şifresini kontrol eder.
        Eğer doğruysa JWT formatında bir Access Token döndürür.
        """
    #Veritabanından, girilen e-posta adresine sahip kullanıcıyı buluyoruz
    user=crud_user.get_user_by_email(db, email=user_in.email)

    #Kullanıcı hiç yoksa veya şifresi (hashlenmiş haliyle) eşleşmiyorsa 401 hatası veriyoruz
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401,detail="E-posta veya şifre hatalı")

     # Bilgiler doğruysa token içine koyacağımız veriyi (Payload) hazırlıyoruz
     #sub (subject) alanına kullanıcının ID'sini ekliyoruz ki dependencies.py'de kim olduğunu
    token_data = {"sub": str(user.id)}

    access_token = create_access_token(data=token_data)

    refresh_token = security.create_refresh_token(data=token_data)

    #frontendin tokeni alıp kullanabilmesi için json
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }



@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    Giriş yapmış kullanıcının profil bilgilerini getirir.
    """
    return current_user

@router.put("/me",response_model=UserResponse)
def update_profile(user_in: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
        Giriş yapmış kullanıcının KENDİ profil bilgilerini günceller.
        Token kime aitse, onun bilgileri değişir.
        """
    #kullanıcı mail değiştirmek istiyosa o mail başkasına ait mi değil mi kontrolu
    if  user_in.email and user_in.email != current_user.email:
        if crud_user.get_user_by_email(db, email=user_in.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Bu email bir başkası tarafından kullanılıyor")

    #kullanıcı username değiştirmek istiyoken bu username başkasına ait mi kontrolü
    if user_in.username and user_in.username != current_user.username:
        if crud_user.get_user_by_username(db, username=user_in.username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Bu kullanıcı adı zaten alınmış")

    updated_user=crud_user.update_user(db=db,db_user=current_user,user_in=user_in)
    return updated_user

@router.get("/search", response_model=list[UserResponse])
def search_users(q: str = "", db: Session = Depends(get_db)):
    """
    Kullanıcı adında geçen kelimeye göre arama yapar.
    """
    if not q:
        return []
    return crud_user.search_users(db, query=q, limit=5)

@router.get("/{user_id}", response_model=UserResponse)
def get_user_profile(user_id: str, db: Session = Depends(get_db)):
    """
    Belirli bir kullanıcının profil bilgilerini getirir.
    Herkese açıktır (Token gerekmez).
    """
    user = crud_user.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı Bulunamadı")
    return user

@router.get("/{user_id}/stats", response_model=UserStatsResponse)
def get_user_stats(user_id: str, db: Session = Depends(get_db)):
    """
    Belirli bir yazarın kapsamlı istatistiklerini getirir.
    Herkese açıktır (Token gerekmez).
    """
    # 1. Kullanıcı ID'ye göre sistemde var mı diye kontrol et
    user = crud_user.get_user_by_id(db, user_id=user_id) # veya senin crud'daki ID ile arama fonksiyonun
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı Bulunamadı")

    # 2. İstatistikleri hesapla ve döndür
    stats = crud_stats.get_user_statistics(db=db, user_id=user.id)
    return stats

@router.post("/refresh")
def refresh_access_token(
    refresh_token: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
        Süresi dolan access_token'ı yenilemek için kullanılır.
        Geçerli bir refresh_token gönderildiğinde yeni bir access_token ve refresh_token döner.
        """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Geçersiz veya süresi dolmuş refresh token",
    )

    try:
        #tokeni çöz ve içindeki paylodı al(veriler)
        payload=jwt.decode(
            refresh_token,
            security.settings.SECRET_KEY,
            algorithms=[security.settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        #içinde kullanıcı id si yoksa veya tipi refresh değilse reddet
        if user_id is None or token_type != "refresh":
            raise credentials_exception

    except Exception:
        #token bozuksa veya süresi dolmuşsa hata fırlatır
        raise credentials_exception

    #kullanıcı hala db de mi bak
    user=db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    #her şey tamamsa acces ve refresh üret
    token_data={"sub": str(user.id)}
    new_access_token = security.create_access_token(data=token_data)
    new_refresh_token = security.create_refresh_token(data=token_data)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }