from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from app.api.dependencies import get_db, get_current_user
from app.models.follow import Follow
from app.models.user import User
from app.schemas.follow import FollowResponse
router = APIRouter()

#kullanıcı takip etme
@router.post("/{user_id}",response_model=FollowResponse,status_code=status.HTTP_201_CREATED)
def follow_user(
        user_id: str, #takip edilecek kişinin id si
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
        Belirli bir kullanıcıyı takip eder.
        """
    #kullanıcı kendi kendini takip edemez
    if current_user.id==user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST_UNAUTHORIZED,detail="Kendi kendini takip edemezsin")

    #takip edilecek kişi gerçekten var mı
    user_to_follow=db.scalar(select(User).where(User.id == user_id))
    if not user_to_follow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Kullanıcı bulunamadı")

    #kullanıcı zaten takip ediliyor mu
    existing_follow = db.scalar(
        select(Follow).where(Follow.follower_id == current_user.id, Follow.following_id == user_id)
    )
    if existing_follow:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Kullanıcı zaten takip ediliyor")

    #her şey okeyse takip et
    new_follow = Follow(
        follower_id=current_user.id,
        following_id=user_id,
    )
    db.add(new_follow)
    db.commit()
    db.refresh(new_follow)

    return new_follow
#takibi bırakma (delete)
@router.delete("/{user_id}",status_code=status.HTTP_204_NO_CONTENT)
def unfollow_user(
        user_id:str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
        Belirli bir kullanıcıyı takipten çıkarır.
        """
    follow_record = db.scalar(
        select(Follow).where(Follow.follower_id == current_user.id, Follow.following_id == user_id)
    )
    if not follow_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Bu kullanıcıyı zaten takip etmiyorsunuz")

    db.delete(follow_record)
    db.commit()

    return None

#bir kullanıcının takipçilerini listele
@router.get("/{user_id}/followers",response_model=List[FollowResponse])
def get_user_followers(
        user_id: str,
        db: Session = Depends(get_db),
):
    """
        Belirli bir kullanıcının takipçilerini getirir.
        """
    #kullanıcı var mı kontrolü
    user=db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Kullanıcı bulunamadı")

    # following_id si bu kullanıcı olan kayıtları getir
    followers = db.scalars(select(Follow).where(Follow.following_id == user_id)).all()
    return followers

#Bir kullanıcının takip ettiklerini listeleme
@router.get("/{user_id}/following",response_model=List[FollowResponse])
def get_user_following(
        user_id: str,
        db: Session = Depends(get_db),
):
    """
        Belirli bir kullanıcının takip ettiği kişileri getirir.
        (O kimleri takip ediyor?)
        """
    user=db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Kullanıcı bulunamadı")

    #follower id si bu kullanıcı olanları getir
    following = db.scalars(select(Follow).where(Follow.follower_id == user_id)).all()
    return following