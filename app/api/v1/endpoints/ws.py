import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.websockets.manager import manager
from app.models.message import Message
from app.api.dependencies import get_db,get_current_user_ws
from app.models.user import User

router = APIRouter()

@router.websocket("/{user_id}")
async def websocket_endpoint(
        websocket: WebSocket,
        user_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_ws)
):
    """
        Kullanıcı sisteme giriş yaptığında (veya sayfayı açtığında)
        bu endpointe bağlanarak sürekli açık bir iletişim kanalı kurar.
        """

    # Eğer başkasının chatine girmeye çalışıyorsa bağlantıyı reddet
    if current_user.id != user_id:
        from fastapi import status
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return


    #istek atan kullanıcıyı manager listesine ekle ve bağlantıyı onayla
    await manager.connect(websocket,user_id)

    try:
        while True:
            #istemciden bize mesaj gelirse diye dinliyoruz,string bekle
            data = await websocket.receive_text()

            try:
                #gelen metni jsondan dict e çevir
                payload = json.loads(data)
                #json içindeki action tipini oku
                action = payload.get("action")

                #kullanıcı mesaj yazıyo
                if action == "typing":
                    reciever_id=payload.get("reciever_id")

                    #hedef kullanıcıya anında haber yolla(receiver_id)
                    await manager.send_personal_message({"type": "typing", "sender_id": user_id},reciever_id)

                #kullanıcı mesajları gördü
                elif action == "mark_read":
                    sender_id=payload.get("sender_id") #kimin mesajı okundu

                    # Bana mesajı atan kişi (sender_id) buysa
                    # ve henüz okunmamış (is_read == False) olan tüm mesajları bul diyor
                    # update ile bulunan  satırların 'is_read' değeri topluca true yapılır
                    db.query(Message).filter(
                        Message.sender_id == sender_id,
                        Message.is_read == False
                    ).update({"is_read": True})

                    db.commit()



                    #karşı tarafa mesajın okundu bilgisi yollandı
                    await manager.send_personal_message({"type": "message_read", "reader_id": user_id},sender_id)

            except json.JSONDecodeError:
                pass #hatalıysa pass, sistemi çökertme



    except WebSocketDisconnect:

        manager.disconnect(websocket, user_id)
