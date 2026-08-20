from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.conversation import Conversation
from app.models.message import Message

def create_message(db: Session, conversation_id: str, sender_id: str, content: str) -> Message:
    """
    Kullanıcının gönderdiği mesajı 'Message' tablosuna kaydeder.
    """
    #yeni mesaj modeli oluştur
    new_message = Message(conversation_id=conversation_id,sender_id=sender_id, content=content)

    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return new_message

def get_conversation_messages(db: Session, conversation_id: str,skip: int = 0, limit: int = 10):
    """
    İçine girdiğimiz bir sohbet odasındaki (conversation_id) tüm geçmiş mesajları getirir.
    """
    query=select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.desc()).offset(skip).limit(limit)

    return db.scalars(query).all()