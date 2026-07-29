from pydantic import BaseModel

class TagResponse(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True