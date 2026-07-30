from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.post import Post
from app.models.follow import Follow
from app.schemas.post import PostCreate, PostUpdate
from app.models.tag import Tag
import re
import unicodedata

def generate_slug(title: str) -> str:
    """Başlığı SEO dostu bir URL formatına (slug) çevirir."""
    # 1. Türkçe karakterleri (ş, ğ, ü, ö, ç, ı) İngilizce karşılıklarına dönüştür
    text = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode('utf-8')
    # 2. Harf, rakam, boşluk ve tire DIŞINDAKİ tüm özel karakterleri sil
    text = re.sub(r'[^\w\s-]', '', text.lower())
    # 3. Birden fazla boşluğu veya tireyi tek bir tireye (-) dönüştür
    return re.sub(r'[-\s]+', '-', text).strip('-')





def get_post_by_id(db: Session, post_id: str) -> Post | None:
    """ID'ye göre veritabanından tek bir makale getirir."""
    return db.scalar(select(Post).where(Post.id == post_id))



def get_posts(db: Session,skip: int = 0, limit: int = 10,search:str="",tag:str=None,author_username:str=None):
    """Tüm makaleleri sayfalama ve arama filtreleriyle çeker."""

    #temel sorguyu başlat
    query = select(Post).where(Post.status == "published")

    #Eğer kullanıcı bir arama kelimesi gönderdiyse filtrele
    if search:
        # ilike: büyük/küçük harf duyarsız arama yapar
        # f"%{search}%": Kelimenin başında veya sonunda başka harfler de olabilir demek
        query = query.where(Post.title.ilike(f"%{search}%"))

    if tag:
        clean_tag = tag.strip().lower()
        query = query.where(Post.tags.any(Tag.name == clean_tag))

    #yazara göre filtreleme
    # Eğer dışarıdan bir yazar kullanıcı adı (author_username) gönderilmişse, sorguyu ona göre daraltıyoruz.
    # Post modelindeki 'author' ilişkisini (relationship) kullanarak User modeline ulaşıyor ve username'i kontrol ediyoruz.
    if author_username:
           query = query.where(Post.author.has(username=author_username))



    #Sayfalama ayarlarını ekle ve en yeniden en eskiye sırala
    query = query.offset(skip).limit(limit).order_by(Post.created_at.desc())

     #Sorguyu çalıştır ve döndür
    return db.scalars(query).all()

def get_post_by_slug(db: Session, slug: str) -> Post:
    """Makaleyi URL'deki slug'ına göre getirir."""
    return db.scalar(select(Post).where(Post.slug == slug))


def create_post(db: Session, post_in: PostCreate, author_id: str) -> Post:
    """Yeni makaleyi veritabanına kaydeder, otomatik slug üretir ve etiketleri bağlar."""

    #SLUG ÜRETİMİ VE ÇAKIŞMA KONTROLÜ
    base_slug = generate_slug(post_in.title)
    unique_slug = base_slug
    counter = 1

    # Veritabanında bu slug'dan zaten var mı diye bak (Örn: "ilk-makalem")
    # Varsa sonuna rakam ekleyerek tekrar dene (Örn: "ilk-makalem-1", "ilk-makalem-2")
    while db.scalar(select(Post).where(Post.slug == unique_slug)):
        unique_slug = f"{base_slug}-{counter}"
        counter += 1


    new_post = Post(
        title=post_in.title,
        content=post_in.content,
        author_id=author_id,
        status=post_in.status,
        slug=unique_slug,
    )
    #Tag işlemleri
    if post_in.tags:
        for tag_name in post_in.tags:
            # Kullanıcının gönderdiği kelimeyi küçük harfe çevirip boşluklarını temizle
            clean_tag_name = tag_name.lower().strip()
            #böyle bir etiket var mı bak
            existing_tag=db.scalar(select(Tag).where(Tag.name == clean_tag_name))
            if existing_tag:
                #varsa mevcut etiketi makaleye ekle
                new_post.tags.append(existing_tag)
                #yoksa yenisini oluştur ve makaleye ekle
            else:
                new_tag=Tag(name=clean_tag_name)
                new_post.tags.append(new_tag)

    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

def update_post(db: Session, db_post: Post, post_in: PostUpdate) -> Post:
    """Mevcut bir makalenin başlık veya içeriğini günceller."""
    if post_in.title is not None:
        db_post.title = post_in.title
    if post_in.content is not None:
        db_post.content = post_in.content

    #tag güncelleme mantığı
    # Eğer kullanıcı 'tags' alanı gönderdiyse (boş liste [] bile gönderse bu if çalışır)
    if post_in.tags is not None:
        #önce makalenin mevcut etiketlerini temizle
        db_post.tags.clear()

        #sonra yeni gönderilenleri tek tek ekle
        for tag_name in post_in.tags:
            clean_tag_name = tag_name.lower().strip()
            existing_tag=db.scalar(select(Tag).where(Tag.name == clean_tag_name))

            if existing_tag:
                db_post.tags.append(existing_tag)
            else:
                new_tag=Tag(name=clean_tag_name)
                db_post.tags.append(new_tag)

    db.commit()
    db.refresh(db_post)
    return db_post

def delete_post(db: Session, db_post: Post):
    """Makaleyi veritabanından kalıcı olarak siler."""
    db.delete(db_post)
    db.commit()

def get_feed_posts(db: Session, user_id: str):
    """Kullanıcının sadece takip ettiği kişilerin makalelerini getirir."""
    following_ids = db.scalars(
        select(Follow.following_id).where(Follow.follower_id == user_id)
    ).all()

    if not following_ids:
        return []

    return db.scalars(
        select(Post)
        .where(Post.author_id.in_(following_ids))
        .order_by(Post.created_at.desc())
    ).all()


def get_user_drafts(db: Session, user_id: str,skip: int = 0, limit: int = 10):
    """giriş yapan kullanıcının taslaklarını getir(draft)"""
    return db.scalars(
        select(Post)
        .where(Post.author_id == user_id, Post.status == "draft")
        .order_by(Post.created_at.desc())
        .offset(skip)
        .limit(limit)
    ).all()


