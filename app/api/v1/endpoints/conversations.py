from fastapi import APIRouter, Depends,Query
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.conversation import ConversationResponse
from app.crud.crud_conversation import get_user_conversations
from app.crud.crud_message import get_conversation_messages
from fastapi import HTTPException
from app.models.conversation import Conversation

router = APIRouter()

@router.get("",response_model=List[ConversationResponse])
def get_conversations(
        skip:int=Query(0),
        limit:int=Query(10),
        db:Session = Depends(get_db),
        current_user:User = Depends(get_current_user)):
    """
      Kullanıcının yan panelinde  gözükecek olan sohbet listesini oluşturur.
      Karşı tarafın profil resmi ve o sohbette atılan son mesajın bir önizlemesi döner.
      """
    conversations=get_user_conversations(db,current_user.id,skip,limit)

    result=[]

    #Her bir sohbet odası için döngüye gir
    for c in conversations:

        # Eğer odadaki 1. kişi bizsek, karşı taraf 2. kişidir (c.user2),aksi halde 1. kişidir (c.user1)
        other_user = c.user2 if c.user1_id == current_user.id else c.user1

        # Son mesaj önizlemesi
        messages = get_conversation_messages(db, c.id,skip=0,limit=10)

        # messages listesi boş değilse  listenin en son elemanını (messages[-1]) alınır
        last_message = messages[0] if messages else None

        #karşı tarafın attığı ve henüz okyunmamış mesajları say
        unread_count = sum(1 for m in messages if m.sender_id == other_user.id and not m.is_read)

        # Şemaya (ConversationResponse) uygun olarak bir dict inşa edip listeye ekle
        result.append({
            "id": c.id,
            "user1_id": c.user1_id,
            "user2_id": c.user2_id,


            "other_user": {
                "id": other_user.id,
                "username": other_user.username,
                "profile_image_url": other_user.profile_image_url
            },

            # Sohbet sırasını belirleyen asıl değer
            "last_message_at": c.last_message_at,

            # Varsa mesaj içeriği, yoksa None
            "last_message_content": last_message.content if last_message else None,
            "unread_count": unread_count
        })

    return result

@router.delete("/{conversation_id}")
def delete_conversation(
        conversation_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    #sohbeti veritabanından bul
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()

    # Sohbet yoksa
    if not conv:
        raise HTTPException(status_code=404, detail="Sohbet bulunamadı.")

    # Eğer bu başkasının sohbetiyse silmeyi engelle
    if conv.user1_id != current_user.id and conv.user2_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bu sohbeti silme yetkiniz yok.")

    # Sohbeti  sil
    db.delete(conv)
    db.commit()

    return {"message": "Sohbet başarıyla silindi."}

