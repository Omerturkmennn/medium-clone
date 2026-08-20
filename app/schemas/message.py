from pydantic import BaseModel, ConfigDict
from datetime import datetime

#mesaj yollanırken frontenden gelecek verinin yapısı
class MessageCreate(BaseModel):
    receiver_id: str
    content: str

#apiden frontende donecek verinin yapısı
class MessageResponse(BaseModel):
    id: str
    sender_id: str
    receiver_id: str  #Frontendin mesajın kime gittiğini bilmesi için
    content: str
    is_read: bool
    created_at: datetime

    #alchemy modelini pydantice dönüştür
    model_config = ConfigDict(from_attributes=True)