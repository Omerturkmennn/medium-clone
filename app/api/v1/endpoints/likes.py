from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from sqlalchemy.sql.functions import current_user

from app.api.dependencies import get_db, get_current_user
from app.models.like import Like
from app.models.post import Post
from app.models.user import User
from app.schemas.like import LikeResponse

router = APIRouter()

#makaleyi beğenme

@router.post("/post/{post_id}",response_model=LikeResponse,status_code=status.HTTP_201_CREATED)
def like_post(
        post_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
        Belirli bir makaleye beğeni (like) atar.
        Kullanıcı aynı makaleyi sadece 1 kez beğenebilir.
        """
    #makale var mı
    post=db.scalar(select(Post).where(Post.id == post_id))
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Makale bulunamadı")

    #kullanıcı makaleyi daha önce beğenmiş mi
    existing_like = db.scalar(
        select(Like).where(Like.post_id == post_id, Like.user_id == current_user.id)
    )
    if existing_like:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="bu makaleyi zaten beğendiniz")

    #her şey yolundaysa beğeniyi oluştur
    new_like = Like(
        post_id=post_id,
        user_id=current_user.id,
    )
    db.add(new_like)
    db.commit()
    db.refresh(new_like)

    return new_like

@router.delete("/post/{post_id}",status_code=status.HTTP_204_NO_CONTENT)
def unlike_post(
        post_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
        Belirli bir makaledeki beğeniyi geri alır (siler).
        """
    #Kullanıcının bu makaleye ait beğenisini bul
    like_to_remove = db.scalar(select(Like).where(Like.post_id == post_id),Like.user_id == current_user.id)

    if not like_to_remove:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Bu makalede size ait beğeni bulunamadı")

    db.delete(like_to_remove)
    db.commit()

    return None

#makalenin beğenilerini listle
@router.get("/posts/{post_id}",response_model=List[LikeResponse])
def get_likes_for_post(
        post_id: str,
        db: Session = Depends(get_db),
):
    """
        Belirli bir makaleye ait tüm beğenileri listeler.
        Böylece Frontend tarafında beğenilerin uzunluğunu (len) alarak "Toplam Beğeni Sayısı"nı gösterebiliriz.
        """
    post=db.scalar(select(Post).where(Post.id == post_id))
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Makale Bulunamadı")

    likes = db.scalars(select(Like).where(Like.post_id == post_id)).all()
    return likes