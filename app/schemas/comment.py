from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.schemas.user import UserResponse

#Ortak Alanlar (Hem oluştururken hem okurken gereken temel alan)
class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class CommentUpdate(CommentBase):
    content: str | None= None

#API den frontende donecek yorum şeması
class CommentResponse(CommentBase):
    id: str
    author_id: str
    post_id: str
    created_at: datetime
    updated_at: datetime
    author: UserResponse | None = None

    model_config = ConfigDict(from_attributes=True)
