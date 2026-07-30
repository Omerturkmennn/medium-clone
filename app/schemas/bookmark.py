from pydantic import BaseModel
from datetime import datetime

class BookmarkResponse(BaseModel):
    id: str
    user_id: str
    post_id: str
    created_at: datetime

    class Config:
        from_attributes = True