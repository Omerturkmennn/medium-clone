from fastapi import APIRouter, Depends, status,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from app.api.dependencies import get_db, get_current_user
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostResponse,PostUpdate

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

#Makale güncelleme
@router.put("/{post_id}", response_model=PostResponse)

def update_post(
        #URLden güncellenecek makalenin ID'sini al
        post_id: str,

        #kullanıcının gönderdiği yeni içerik verisi
        post_in: PostUpdate,

        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
        Belirli bir makaleyi günceller.
        YETKİ KONTROLÜ: Sadece makalenin sahibi (yazarı) güncelleyebilir.
        """
    #db de bize verilen id ye sahip makale var mı bakıyoruz
    post=db.scalar(select(Post).where(Post.id == post_id))

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Makale bulunamadı")

    #Güvenlik: Makaleyi yazan kişinin ID'si ile istek atan kişinin (token) ID'si aynı mı
    if post.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Bu Makaleyi güncelleme yetkiniz yok")

    #Kullanıcı sadece başlığı veya sadece içeriği değiştirmek isteyebilir.
    # Hangisi Pydantic şemasından (post_in) dolu geldiyse onu güncelliyoruz.
    if post_in.title is not None:
        post.title = post_in.title
    if post_in.content is not None:
        post.content = post_in.content

    db.commit()
    db.refresh(post)
    return post

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
        post_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
        Belirli bir makaleyi kalıcı olarak siler.
        YETKİ KONTROLÜ: Sadece makalenin sahibi silebilir.
        """
    #silinecel makaleyi db den bul
    post=db.scalar(select(Post).where(Post.id == post_id))

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Makale bulunamadı")

    #silecek kişinin makalesi mi kontrolü
    if post.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Bu Makaleyi silme yetkiniz yok!")

    #makaleyi sil
    db.delete(post)
    db.commit()

    #HTTP_204_NO_CONTENT kodu:işlem başarıyla yapıldı ama sana geri döndüreceğim bir veri (JSON) kalmadı demektir
    return None