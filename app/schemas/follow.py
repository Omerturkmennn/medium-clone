from pydantic import BaseModel, ConfigDict
from datetime import datetime

class UserBasicInfo(BaseModel):
    id:str
    username:str

    model_config = ConfigDict(from_attributes=True)


#Sadece Frontende döneceğimiz veri yapısı
class FollowResponse(BaseModel):
    id:str
    follower_id:str
    following_id:str
    created_at:datetime

    follower_user: UserBasicInfo
    following_user: UserBasicInfo

   #Alchemy modelini Pydanticee dönüştürmek için gerekli ayar
    model_config = ConfigDict(from_attributes=True)