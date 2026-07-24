from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    username:str = Field(..., min_length=5, max_length=50, description="Kullanıcı adı 5-50 karakter arasında olmalıdır!")
    bio:Optional[str]=None
    profile_image_url:Optional[str]=None

#kullanıcı oluştur
class UserCreate(UserBase):
    password: str =Field(..., min_length=6, max_length=128, description="Şifre en az 8 haneli olmalı")

#dışarıya dönülecek veri
class UserResponse(UserBase):
    id:str
    is_active:bool
    created_at:datetime
    updated_at:datetime

    #SQLAlchemy modelini Pydantic modeline dönüştürebilmek için
    model_config = ConfigDict(from_attributes=True)
