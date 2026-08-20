from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


#Karşı tarafın temel bilgilerini dönmek için ufak  şema
class ConversationUserResponse(BaseModel):
    id: str
    username: str
    profile_image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# WhatsApp tarzı sohbet listesinde dönülecek veri şeması
class ConversationResponse(BaseModel):
    id: str
    user1_id: str
    user2_id: str
    other_user: ConversationUserResponse  # Sohbet edilen diğer kişinin detayları
    last_message_at: Optional[datetime]
    last_message_content: Optional[str] = None
    unread_count: int = 0

    model_config = ConfigDict(from_attributes=True)
