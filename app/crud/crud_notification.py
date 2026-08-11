from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.notification import Notification

def create_notification(db:Session,user_id:str,message:str, action_url:str=None)->Notification:
    """
        Veritabanına yeni bir bildirim kaydeder.
        Bu fonksiyon arka planda, WebSocket mesajı gönderilmeden hemen önce çalışacak.
        """
    new_notification = Notification(user_id=user_id,message=message, action_url=action_url)
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return new_notification

def get_user_notifications(db: Session, user_id: str, skip: int = 0, limit: int = 20):
    """Kullanıcının geçmiş bildirimlerini en yeniden en eskiye sıralayarak getirir."""

    return  db.scalars(
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .offset(skip)
        .limit(limit)
    ).all()

def mark_as_read(db: Session, notification_id: str)->Notification | None:
    """
        Belirli bir bildirimi bularak 'is_read' durumunu True yapar.
        Kullanıcı bildirime tıkladığında çalışacak.
        """
    notification=db.scalar(select(Notification).where(Notification.id == notification_id))
    if notification:
        notification.is_read = True
        db.commit()
        db.refresh(notification)
    return notification


