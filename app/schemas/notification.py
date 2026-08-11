from pydantic import BaseModel, ConfigDict
from datetime import datetime

class NotificationResponse(BaseModel):
    id:str
    user_id:str
    message:str
    is_read:bool
    created_at:datetime
    action_url:str | None = None

    #Alchemy modelini Pydantice dönüştürme
    model_config = ConfigDict(from_attributes=True)