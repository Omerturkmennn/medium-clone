from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from app.api.dependencies import get_db, get_current_user
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostResponse

router = APIRouter()


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
        # İstemciden (Postman veya Swagger üzerinden) gelen başlık ve içerik bilgilerini alıyoruz.
        post_in: PostCreate,

        # Veritabanı ile konuşabilmek için dependencies.py'den oturum (Session) açıyoruz.
        db: Session = Depends(get_db),


        # Depends(get_current_user) çalıştığı an, sistem gelen isteğin başlığındaki
        # Bearer token'a bakar. Token'ı çözer, veritabanından o kişiyi bulur ve
        # tüm bilgilerini 'current_user' değişkeninin içine doldurur.
        # Eğer token yoksa veya süresi dolmuşsa, kod buraya hiç inmeden otomatik 401 hatası fırlatır.
        current_user: User = Depends(get_current_user)
):
    """
        Yeni bir makale oluşturur.
        Yalnızca geçerli bir token'a sahip (giriş yapmış) kullanıcılar bu işlemi yapabilir.
        """
    # SQLAlchemy kullanarak veritabanına eklenecek yeni makale satırını hazırla
    new_post = Post(
        title=post_in.title,
        content=post_in.content,

        # Makalenin yazarını dışarıdan istemiyoruz Sisteme kim giriş yaptıysa
        # (token kime aitse) o kişinin ID sini otomatik olarak çekip buraya yazıyoruz.
        # Bu başkasının adına makale yazılmasını engelleyen  bir güvenlik kuralıdır
        author_id=current_user.id
    )

    # Hazırladığımız nesneyi veritabanı işlem sırasına (RAM e) ekliyoruz.
    db.add(new_post)

    # İşlemi onaylıyor ve veritabanına kalıcı olarak yazıyoruz
    db.commit()

    # Veritabanı, makaleyi kaydederken ona otomatik bir benzersiz 'id' ve 'created_at' (tarih) atadı.
    # refresh() komutu ile bu yeni atanan veritabanı bilgilerini 'new_post' nesnemizin içine geri çekiyoruz
    # ki return dediğimizde kullanıcı (frontend) bu bilgileri eksiksiz görebilsin.
    db.refresh(new_post)

    return new_post

@router.get("/", response_model=List[PostResponse])
def get_posts(

        # Burada sadece veritabanı bağlantısı istiyoruz.
        #  'current_user = Depends(...)' kısmını bilerek eklemedik
        # Çünkü makaleleri herkes okuyabilir, giriş yapmaya (token'a) gerek yoktur.
         db: Session = Depends(get_db),

):
    """
        Sistemdeki tüm makaleleri liste halinde döndürür.
        Herkese açık Endpoint
        """
    # Veritabanındaki Post tablosuna gidip tüm satırları çeken SQL sorgusunu çalıştırıyoruz.
    # scalars() -> veritabanından gelen karmaşık satırları temiz, tek boyutlu bir liste yapar
    posts = db.scalars(select(Post)).all()

    return posts