from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_db, get_current_user
from app.models.bookmark import Bookmark
from app.models.user import User
from app.schemas.bookmark import BookmarkResponse
from app.crud import crud_bookmark, crud_post

router = APIRouter()

#makaleyi okuma listesine ekleme endpointi
@router.post("/post/{post_id}",response_model=BookmarkResponse,status_code=status.HTTP_201_CREATED)
def bookmark_post(post_id:str, # URL'den kaydedilecek makalenin ID'sini alıyoruz
                  db:Session = Depends(get_db),
                  current_user:User = Depends(get_current_user),# İşlemi yapan giriş yapmış (token sahibi) kullanıcı
):
    """
        Belirli bir makaleyi okuma listesine (bookmarks) ekler.
        Kullanıcı aynı makaleyi sadece 1 kez kaydedebilir.
        """
    post=crud_post.get_post_by_id(db,post_id=post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Makale bulunamadı")

    #Kullanıcı bu makaleyi daha önce kaydetmiş mi diye bak
    existing_bookmark=crud_bookmark.get_bookmark(db=db,post_id=post_id,user_id=current_user.id)
    if existing_bookmark:
        return existing_bookmark

    #makaleyi kullanıcının listesine ekle
    new_bookmark=crud_bookmark.create_bookmark(db=db,post_id=post_id,user_id=current_user.id)
    return new_bookmark

#okuma listesinden cıkarma.(bookmark silme)
@router.delete("/post/{post_id}",status_code=status.HTTP_204_NO_CONTENT)
def unbookmark_post(post_id:str, db:Session = Depends(get_db),current_user:User = Depends(get_current_user)):
    """
        Belirli bir makaleyi okuma listesinden çıkarır.
        """
    #silinmek istenen kaydı db den bul
    bookmart_to_remove=crud_bookmark.get_bookmark(db=db,post_id=post_id,user_id=current_user.id)

    if not bookmart_to_remove:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Makale okuma listenizde bulunmuyor")

    #kaydı db den sil
    crud_bookmark.delete_bookmark(db=db,db_bookmark=bookmart_to_remove)
    return None

#kaydedilen makaleleri listeleme
@router.get("/",response_model=List[BookmarkResponse])
def get_user_bookmarks(db:Session=Depends(get_db),current_user:User = Depends(get_current_user)):
    """
        Giriş yapan kullanıcının okuma listesini (kaydettiği makaleleri) getirir.
        """
    #sadece istek atan  kişinini kaydettiği  makaleleri getir
    bookmarks=crud_bookmark.get_user_bookmarks(db=db,user_id=current_user.id)
    return bookmarks

