from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.crud import crud_notification

router = APIRouter()

#kullanıcının bildirimlerini listeleme endpointi
@router.get("/", response_model=List[NotificationResponse])
def get_my_notifications(
        skip: int = 0,
        limit: int = 20,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
        Giriş yapan kullanıcının tüm bildirimlerini (Geçmiş Bildirimler) getirir.
        Sadece kendi bildirimlerini görebilir.
        """
    return crud_notification.get_user_notifications(db=db,user_id=current_user.id,skip=skip,limit=limit)

#bildirimi okundu işaretleyen endpoint
@router.put("{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
        notification_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
        Belirli bir bildirimi okundu olarak (is_read = True) işaretler.
        """

    #önce bildirimi db de bul ve güncelle
    notification=crud_notification.mark_as_read(db=db,notification_id=notification_id)

    if not notification:
        return None

    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bu bildirimi okuma yetkiniz yok")

    return notification
