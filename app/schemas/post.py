from pydantic import BaseModel, ConfigDict,computed_field
from datetime import datetime
from typing import Optional, List
from app.schemas.tag import TagResponse
from enum import Enum


class PostStatus(str, Enum):
    draft = 'draft'
    published = 'published'

#Burdaki kurallar sayesinde API ye boş başlık veya hatalı veri gönderilmesini engellenecek

# Yazı oluşturulurken istemciden sadece başlık ve içerik alınacak
# author_id'yi dışarıdan almayacağız çünkü onu Token'dan (Giriş yapan kişiden) otomatik çekeceğiz
class PostCreate(BaseModel):
    title: str
    content: str
    tags:Optional[List[str]] = []
    status: Optional[PostStatus] = PostStatus.draft
    tldr: Optional[str] = None
    cover_image: Optional[str] = None


#yazı güncellenirken başlık veya içerik opsiyonel olabilri
class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[PostStatus] = None
    cover_image: Optional[str] = None

class PostAuthorResponse(BaseModel):
    id: str
    username: str
    
    model_config = ConfigDict(from_attributes=True)

# API'den dışarıya (Frontende) yazı bilgilerini gönderirken kullanacağımız şema
class PostResponse(BaseModel):
    id: str
    slug:Optional[str]=None
    title: str
    content: str
    tldr: Optional[str] = None
    author_id: str
    author: Optional[PostAuthorResponse] = None
    status: PostStatus
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse]=[]
    cover_image:Optional[str]=None
    like_count: int = 0
    comment_count: int = 0


    # Alchemy modelini Pydantice dönüştürmek için gereken ayar
    model_config = ConfigDict(from_attributes=True)

    #Dinamik okuma süresi hesaplama
    @computed_field
    @property

    def read_time(self)->int:
        """
                Makalenin içeriğindeki kelime sayısını hesaplar ve
                ortalama okuma hızına (200 kelime/dk) bölerek tahmini süreyi döndürür.
                """
        if not self.content:
            return 1

        # İçeriği boşluklardan bölerek kelime listesi oluştur ve sayısını al
        word_count = len(self.content.split())

        #200 e böl ve en yakın tam sayıya yuvarla
        minutes=round(word_count/200)

        #Makale çok kısaysa bile en az 1 dakika okuma süresi dönsün
        return max(1, minutes)