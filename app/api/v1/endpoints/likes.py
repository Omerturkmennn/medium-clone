from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.like import LikeResponse

# CRUD Modülleri
from app.crud import crud_like, crud_post

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
    post = crud_post.get_post_by_id(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Makale bulunamadı")

    #kullanıcı makaleyi daha önce beğenmiş mi
    existing_like = crud_like.get_like(db=db, post_id=post_id, user_id=current_user.id)
    if existing_like: #!!!!!!!!!!!!!!!!
        return existing_like

    #her şey yolundaysa beğeniyi oluştur
    new_like = crud_like.create_like(db=db, post_id=post_id, user_id=current_user.id)
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
    like_to_remove = crud_like.get_like(db=db, post_id=post_id, user_id=current_user.id)

    if not like_to_remove:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Bu makalede size ait beğeni bulunamadı")

    crud_like.delete_like(db=db, db_like=like_to_remove)
    return None

#makalenin beğenilerini listele
@router.get("/posts/{post_id}",response_model=List[LikeResponse])
def get_likes_for_post(
        post_id: str,
        db: Session = Depends(get_db),
):
    """
        Belirli bir makaleye ait tüm beğenileri listeler.
        Böylece Frontend tarafında beğenilerin uzunluğunu (len) alarak "Toplam Beğeni Sayısı"nı gösterebiliriz.
        """
    post = crud_post.get_post_by_id(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Makale Bulunamadı")

    likes = crud_like.get_likes_by_post(db=db, post_id=post_id)
    return likes