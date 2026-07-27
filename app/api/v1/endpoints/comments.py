from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from app.api.dependencies import get_db, get_current_user
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate

router = APIRouter()

#Yorum yapma
@router.post("/post/{post_id}", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
        post_id: str,  # Hangi makaleye yorum yapıldığını URL'den alıyoruz
        comment_in: CommentCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)  #Yorum yapan kişi tokendan geliyor
):
    """
    Belirli bir makaleye yeni bir yorum ekler.
    Giriş yapmış (token sahibi) kullanıcılar kullanabilir.
    """
    #Önce veritabanına bak, böyle bir makale gerçekten var mı diye
    post = db.scalar(select(Post).where(Post.id == post_id))
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Yorum yapılmak istenen makale bulunamadı.")

    #Yorum nesnesini oluştur ve tüm bağlantıları (ilişkileri) kur
    new_comment = Comment(
        content=comment_in.content,
        post_id=post_id,  # URL'den gelen makale kimliği
        author_id=current_user.id  # Token'dan gelen kullanıcı kimliği
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment

#Makale yorumlarını listeleme
@router.get("/post/{post_id}", response_model=List[CommentResponse])
def get_comments_for_posts (post_id: str, db: Session = Depends(get_db)):
    """
        Belirli bir makaleye yapılmış tüm yorumları getirir.
        Okumak herkese açıktır (Token gerekmez).
        """
    post = db.scalar(select(Post).where(Post.id == post_id))
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Makale bulunamadı")

    comments= db.scalars(select(Comment).where(Comment.post_id == post_id)).all()
    return comments

#yorum güncelle
@router.put("/{comment_id}", response_model=CommentResponse)
def update_comment(
        comment_id:str,
        comment_in: CommentUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
        Bir yorumu günceller.
        Sadece yorumun asıl sahibi (yazarı) güncelleyebilir.
        """
    comment = db.scalar(select(Comment).where(Comment.id == comment_id))
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Yorum bulunamadı")

    if comment.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Bu yorumu güncelleme yetkiniz yok")

    if comment_in.content is not None:
        comment.content = comment_in.content

    db.commit()
    db.refresh(comment)
    return comment

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
        comment_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
        Bir yorumu kalıcı olarak siler.
        Sadece yorumun asıl sahibi (yazarı) silebilir.
        """
    comment = db.scalar(select(Comment).where(Comment.id == comment_id))
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Yorum bulunamadi")

    # GÜVENLİK Yorumu silmeye çalışan kişi, yorumun asıl sahibi mi
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Bu yorumu silme yetkiniz yok")
    db.delete(comment)
    db.commit()
    return None

