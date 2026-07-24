from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel

# Yazdığımız veritabanı bağlantısı ve güvenlik fonksiyonlarını içeri alıyoruz
from app.api.dependencies import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import get_password_hash, verify_password, create_access_token

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
def register(user_in:UserCreate, db: Session = Depends(get_db)):
    """
        Yeni bir kullanıcı oluşturur.
        Girilen e-posta veya kullanıcı adı sistemde varsa hata döndürür.
        Şifreyi güvenli bir şekilde hash'leyerek veritabanına kaydeder.
        """
    #e-posta sistemde kayıtlı mı diye kontrol
    user_by_email=db.scalar(select(User).where(User.email==user_in.email))
    if user_by_email:
        raise HTTPException(status_code=400,detail="Bu E-posta zaten kullanılıyor")

    #username sisteme kayıtlı mı kontrolü
    user_by_username=db.scalar(select(User).where(User.username==user_in.username))
    if user_by_username:
        raise HTTPException(status_code=400,detail="Bu kullanıcı adı zaten alınmış")

    #kullanıcının girdiği şifreyi hashle
    hashed_pw=get_password_hash(user_in.password)

    #db ye eklenecek kullanıcı nesnesi
    new_user=User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hashed_pw,
        bio=user_in.bio,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user) # ID, created_at gibi otomatik oluşan verileri nesneye geri yükle

    return new_user

@router.post("/login")
def login_user(user_in: UserLogin, db: Session = Depends(get_db)):
    """
        Kullanıcının e-posta ve şifresini kontrol eder.
        Eğer doğruysa JWT formatında bir Access Token döndürür.
        """
    #Veritabanından, girilen e-posta adresine sahip kullanıcıyı buluyoruz
    user=db.scalar(select(User).where(User.email==user_in.email))

    #Kullanıcı hiç yoksa veya şifresi (hashlenmiş haliyle) eşleşmiyorsa 401 hatası veriyoruz
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401,detail="E-posta veya şifre hatalı")

     # Bilgiler doğruysa token içine koyacağımız veriyi (Payload) hazırlıyoruz
     #sub (subject) alanına kullanıcının ID'sini ekliyoruz ki dependencies.py'de kim olduğunu
    token_data = {"sub": str(user.id)}

    access_token = create_access_token(data=token_data)

    #frontendin tokeni alıp kullanabilmesi için json
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }