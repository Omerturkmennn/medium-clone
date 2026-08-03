from fastapi import APIRouter, Depends, status, HTTPException,File, UploadFile
from sqlalchemy.orm import Session
from typing import List,Optional
import shutil #Dosya kopyalamak için
import uuid #benzersiz dosya isimleri üretmek için

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.post import PostCreate, PostResponse, PostUpdate


from app.crud import crud_post

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
    # Makalenin yazarını dışarıdan istemiyoruz Sisteme kim giriş yaptıysa
    # (token kime aitse) o kişinin ID sini otomatik olarak çekip buraya yazıyoruz.
    # Bu başkasının adına makale yazılmasını engelleyen  bir güvenlik kuralıdır

    # Hazırladığımız nesneyi veritabanı işlem sırasına (RAM e) ekliyoruz.
    # İşlemi onaylıyor ve veritabanına kalıcı olarak yazıyoruz

    # Veritabanı, makaleyi kaydederken ona otomatik bir benzersiz 'id' ve 'created_at' (tarih) atadı.
    # refresh() komutu ile bu yeni atanan veritabanı bilgilerini 'new_post' nesnemizin içine geri çekiyoruz
    # ki return dediğimizde kullanıcı (frontend) bu bilgileri eksiksiz görebilsin.

    # (Yukarıdaki işlemlerin tamamını CRUD fonksiyonuna devrettik)
    new_post = crud_post.create_post(db=db, post_in=post_in, author_id=current_user.id)

    return new_post


@router.get("/", response_model=List[PostResponse])
def get_posts(
        # Burada sadece veritabanı bağlantısı istiyoruz.
        #  'current_user = Depends(...)' kısmını bilerek eklemedik
        # Çünkü makaleleri herkes okuyabilir, giriş yapmaya (token'a) gerek yoktur.
        db: Session = Depends(get_db),

        skip: int = 0,
        limit: int = 10,
        search:Optional[str]="",
        tag:Optional[str]=None,
        author_username:Optional[str]=None
):
    """
            Sistemdeki makaleleri liste halinde döndürür.
            - **skip**: Kaç makale atlanacak (Örn: 2. sayfa için 10 gönderilir)
            - **limit**: Sayfada maksimum kaç makale gösterilecek
            - **search**: Makale başlıklarında kelime araması yapar
            - **tag**: Belirli bir etikete (kategoriye) sahip makaleleri filtreler
            - **author_username**: Sadece belirli bir yazarın makalelerini filtreler
            Herkese açık Endpoint
            """
    # Veritabanındaki Post tablosuna gidip tüm satırları çeken SQL sorgusunu çalıştırıyoruz.
    # scalars() -> veritabanından gelen karmaşık satırları temiz, tek boyutlu bir liste yapar
    posts = crud_post.get_posts(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        tag=tag,
        author_username=author_username
    )

    return posts


# kişiselleştirilmiş feed (ANA SAYFA)
@router.get("/feed", response_model=List[PostResponse])
def get_get_user_feed(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
        Giriş yapan kullanıcının, SADECE takip ettiği yazarların makalelerini getirir.
        (En yeniden en eskiye doğru sıralı olarak)
        """
    # Kullanıcının takip ettiği kişilerin ID'lerini bir liste olarak al
    # kimseyi takip etmiyosa boş liste dön
    # SQL deki  IN operatörü ile sadece bu yazarların makalelerini getir

    feed_posts = crud_post.get_feed_posts(db=db, user_id=current_user.id)

    return feed_posts

@router.get("/me/drafts",response_model=List[PostResponse])
def get_my_drafts(
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
        Giriş yapan kullanıcının henüz yayınlamadığı (taslak/draft) makalelerini listeler.
        Sadece kullanıcının kendisi görebilir.
        """
    drafts=crud_post.get_user_drafts(db=db, user_id=current_user.id,skip=skip,limit=limit)
    return drafts


@router.get("/{slug}", response_model=PostResponse)
def get_post(slug:str, db: Session = Depends(get_db)):
    """
        Belirli bir makaleyi ID yerine Slug ile getirir ve görüntülenme sayısını 1 arttırır.
        Örn: /posts/benim-ilk-makalem
        """
    post=crud_post.get_post_by_slug(db=db, slug=slug)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Makale bulunamadı")

    #makale her çağırıldıgında viewCount sayısını 1 arttırır ve kaydeder
    # EĞER ESKİ BİR MAKALE İSE VE DEĞERİ NONE İSE ÖNCE 0'A EŞİTLE
    if post.view_count is None:
        post.view_count = 0

    # SONRA 1 ARTIR
    post.view_count += 1

    db.commit()
    db.refresh(post)

    return post


# Makale güncelleme
@router.put("/{post_id}", response_model=PostResponse)
def update_post(
        # URLden güncellenecek makalenin ID'sini al
        post_id: str,

        # kullanıcının gönderdiği yeni içerik verisi
        post_in: PostUpdate,

        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
        Belirli bir makaleyi günceller.
        YETKİ KONTROLÜ: Sadece makalenin sahibi (yazarı) güncelleyebilir.
        """
    # db de bize verilen id ye sahip makale var mı bakıyoruz
    post = crud_post.get_post_by_id(db, post_id=post_id)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Makale bulunamadı")

    # Güvenlik: Makaleyi yazan kişinin ID'si ile istek atan kişinin (token) ID'si aynı mı
    if post.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu Makaleyi güncelleme yetkiniz yok")

    # Kullanıcı sadece başlığı veya sadece içeriği değiştirmek isteyebilir.
    # Hangisi Pydantic şemasından (post_in) dolu geldiyse onu güncelliyoruz.
    post = crud_post.update_post(db=db, db_post=post, post_in=post_in)

    return post

#dosya kaydetmek için endpoint
@router.post("/{post_id}/image",response_model=PostResponse)
def upload_post_cover_image(
        post_id: str,
        #kullanıcıdan "file" adında dosya bekliyoruz
        file:UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
        Belirli bir makaleye kapak fotoğrafı yükler.
        Sadece makalenin yazarı bu işlemi yapabilir.
        """
    #Makaleyi veritabanından bul
    post=crud_post.get_post_by_id(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Makale bulunamadı")

    #yetki kontrolu,yüklemeyi yapan kişi makale sahibi mi
    if post.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Sadece kendi makalelerinize fotoğraf yükleyebilirsin ")

    #Dosya adını benzersiz yap (Örn: kapak.jpg yerine 5f3a2b...c1.jpg olacak)
    #Aynı isimde iki dosya yüklenirse birbirini ezmesin diye
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"

    #Dosyanın sunucuda kaydedileceği fiziksel yol
    file_location = f"uploads/{unique_filename}"

    #Dosyayı 'uploads' klasörüne fiziksel olarak kaydet (shutil ile)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    #Veritabanını güncelle: Makalenin cover_image sütununa statik URL'yi yaz
    post.cover_image = f"/static/{unique_filename}"
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
    # silinecel makaleyi db den bul
    post = crud_post.get_post_by_id(db, post_id=post_id)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Makale bulunamadı")

    # silecek kişinin makalesi mi kontrolü
    if post.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu Makaleyi silme yetkiniz yok!")

    # makaleyi sil
    crud_post.delete_post(db=db, db_post=post)

    # HTTP_204_NO_CONTENT kodu:işlem başarıyla yapıldı ama sana geri döndüreceğim bir veri (JSON) kalmadı demektir
    return None