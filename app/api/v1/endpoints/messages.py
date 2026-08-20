
from fastapi import APIRouter, Depends, BackgroundTasks,Query
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.message import MessageCreate, MessageResponse
from app.crud.crud_conversation import get_or_create_conversation
from app.crud.crud_message import create_message, get_conversation_messages
from app.websockets.manager import manager

router = APIRouter()

#async fonk websocket calışıyoken diğer işlemleri blokalmasın
async def send_message_via_ws(message_dict: dict,receiver_id:str):
    """Veritabanına kaydedilen mesajı karşı tarafın websocketine anında yollar."""

    await manager.send_personal_message(message_dict,receiver_id)

@router.post("",response_model=MessageResponse)
async def send_message(
    message_in: MessageCreate,          # Frontend'den gelen veri
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Mesajı atan kişi
):
    """
    Bu endpoint; mesajı alır, yoksa aralarında sohbet odası oluşturur, mesajı veritabanına kaydeder,
    ve ardından anlık olarak WebSocket üzerinden karşı tarafa mesajı fırlatır.
    """

    #sohbet var mı kontrol et yoksa oluştur
    conversation=get_or_create_conversation(db,current_user.id,message_in.receiver_id)

    #mesajı db ye kaydet
    new_message=create_message(db,conversation.id,current_user.id,message_in.content)

    #conversation tablosunu güncelle
    conversation.last_message_at=new_message.created_at
    db.commit()

    #Frontend'e döneceğimiz çıktı formatı
    message_data = {
        "id": new_message.id,
        "sender_id": new_message.sender_id,
        "receiver_id": message_in.receiver_id,
        "content": new_message.content,
        "is_read": new_message.is_read,
        "created_at": new_message.created_at
    }

    # WebSocket için gönderilecek özel veri paketini hazırla
    ws_payload = {
        "type": "new_message",
        "message": {
            "id": new_message.id,
            "sender_id": new_message.sender_id,
            "receiver_id": message_in.receiver_id,
            "content": new_message.content,
            "created_at": new_message.created_at.isoformat(),
            # datetime'ı string'e çeviriyoruz çünkü JSON string bekler
            "is_read": new_message.is_read
        }
    }

    # BackgroundTasks e görev ekle
    # Parametre 1:çalıştırılacak fonksiyon
    # Parametre 2 ve 3: Fonksiyona gidecek argümanlar
    background_tasks.add_task(send_message_via_ws, ws_payload, message_in.receiver_id)

    return message_data

@router.get("/history/{receiver_id}", response_model=List[MessageResponse])
def get_message_history(
        receiver_id: str,
        skip:int=Query(0),
        limit:int=Query(10),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    """
      Belirli bir kişiyle olan geçmiş mesajları baştan sona getirir.
      Sohbetin içine tıklandığında ekranın mesajlarla dolmasını sağlayan fonksiyondur.
      """

    #önce sohbet odası var mı ona bakılır
    conversation=get_or_create_conversation(db,current_user.id,receiver_id)

    #o odaya ait mesajları getir
    messages=get_conversation_messages(db,conversation.id,skip,limit)

    #frontende gidecek liste
    result=[]

    for m in messages:
    # Eğer mesajı atan kişi odadaki 2. kişi ise, alıcı 1. kişidir. Değilse alıcı 2. kişidir
        rec_id=conversation.user1_id if m.sender_id == conversation.user2_id else conversation.user2_id

        result.append({
            "id": m.id,
            "sender_id": m.sender_id,
            "receiver_id": rec_id,
            "content": m.content,
            "is_read": m.is_read,
            "created_at": m.created_at
        })
    return result