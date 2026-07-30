from fastapi import WebSocket

class ConnectionManager(WebSocket):
    def __init__(self):
        # Hangi kullanıcının  hangi WebSocket bağlantılarına sahip olduğunu tutarız
        # Bir kullanıcı aynı anda hem telefondan hem bilgisayardan bağlı olabilir,
        # bu yüzden liste (list[WebSocket]) tutuyoruz.
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self,websocket: WebSocket,user_id:str) :
        #istemciden gelen bağlantıyı kabul et
        await websocket.accept()

        #kullanıcı sözlükte yoksa ona boş bir liste aç
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        #bağlantıyı kullanıcının listesine ekle
        self.active_connections[user_id].append(websocket)

    def disconnect(self,websocket:WebSocket,user_id:str):
        #bağlantı kopunca listeden çıkar
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            #eğer kullanıcının hiçbir bağlantısı kalmadıysa,sözlükten komple sil
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self,message:dict,user_id:str):
        #hedef kullanıcı şuan çevrimiçiyse
        if user_id in self.active_connections:
        # Kullanıcının tüm açık sekmelerine/cihazlarına mesajı JSON olarak gönder
            for connection in self.active_connections[user_id]:
                await connection.send_json(message)

# Bu dosyayı import eden her yerin aynı instance'ı (manager) kullanması için
# nesneyi burada bir kez oluşturuyoruz (Singleton pattern).
manager = ConnectionManager()
