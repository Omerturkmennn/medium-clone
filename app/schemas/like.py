from pydantic import BaseModel, ConfigDict
from datetime import datetime

#Sadece Frontende "Beğeni başarıyla oluştu" derken döndürülecek veri yapısı
class LikeResponse(BaseModel):
    id: str
    user_id: str
    post_id: str
    created_at: datetime

    #SQLAlchemy modelini Pydantice dönüştürmek için gerekli ayar
    model_config = ConfigDict(from_attributes=True)