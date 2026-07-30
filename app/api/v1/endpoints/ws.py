from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websockets.manager import manager

router = APIRouter()

@router.websocket("/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
        Kullanıcı sisteme giriş yaptığında (veya sayfayı açtığında)
        bu endpointe bağlanarak sürekli açık bir iletişim kanalı kurar.
        """
    #istek atan kullanıcıyı manager listesine ekle ve bağlantıyı onayla
    await manager.connect(websocket,user_id)

    try:
        while True:
            #istemciden bize mesaj gelirse diye dinliyoruz
            data = await websocket.receive_text()

    except WebSocketDisconnect:
        #Kullanıcı sekmeyi kapattığında veya interneti koptuğunda
        # exception (hata) fırlatılır.Biz de onu aktif bağlantılar listemizden sileriz
        manager.disconnect(websocket, user_id)
