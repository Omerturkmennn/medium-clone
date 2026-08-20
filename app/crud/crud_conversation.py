from sqlalchemy.orm import Session
from sqlalchemy import select, or_, desc
from app.models.conversation import Conversation

def get_user_conversations(db:Session,user_id:str,skip:int=0,limit:int=10):
    """Kullanıcının dahil olduğu tüm sohbetleri en son mesaja göre sıralayarak getirir."""

    #conversation tablosundan
    query=select(Conversation).where(
        or_(
            Conversation.user1_id == user_id,
            Conversation.user2_id == user_id,
        )
    ).order_by(desc(Conversation.last_message_at)).offset(skip).limit(limit)

    #sonucu liste halinde dondur
    return db.scalars(query).all()

def get_or_create_conversation(db: Session, user1_id: str, user2_id: str) -> Conversation:
    """
    İki kullanıcı arasındaki sohbeti getirir.
    Eğer bu iki kişi daha önce hiç mesajlaşmadıysa, önce veritabanında yeni bir sohbet  oluşturur, sonra onu döndürür.
    """

    #mevcut sohbet var mı kontrol
    query = select(Conversation).where(
        or_(
            (Conversation.user1_id == user1_id) & (Conversation.user2_id == user2_id),
            (Conversation.user1_id == user2_id) & (Conversation.user2_id == user1_id)
        )
    )
    #sorgudan 1 tane sonuç dönmesini istiyoruz.eşleşme yoksa None döner
    conversation =db.scalar(query)

    ## Eğer conversation None geldiyse (daha önce hiç mesajlaşılmadıysa) yeni oluştur
    if not conversation:

        #yeni obje oluştur
        conversation = Conversation(user1_id=user1_id, user2_id=user2_id)

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    return conversation