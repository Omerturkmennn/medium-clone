from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from app.schemas.tag import TagResponse

#Burdaki kurallar sayesinde API ye boş başlık veya hatalı veri gönderilmesini engellenecek

# Yazı oluşturulurken istemciden sadece başlık ve içerik alınacak
# author_id'yi dışarıdan almayacağız çünkü onu Token'dan (Giriş yapan kişiden) otomatik çekeceğiz
class PostCreate(BaseModel):
    title: str
    content: str
    tags:Optional[List[str]] = []

#yazı güncellenirken başlık veya içerik opsiyonel olabilri
class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None

# API'den dışarıya (Frontende) yazı bilgilerini gönderirken kullanacağımız şema
class PostResponse(BaseModel):
    id: str
    title: str
    content: str
    author_id: str
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse]=[]

    # Alchemy modelini Pydantice dönüştürmek için gereken ayar
    model_config = ConfigDict(from_attributes=True)
