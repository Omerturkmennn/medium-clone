from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_db
from app.schemas.tag import TagResponse
from app.crud import crud_tag

router = APIRouter()

@router.get("/", response_model=List[TagResponse])
def get_tags(limit: int = 20, db: Session = Depends(get_db)):
    """
    Sistemdeki en popüler etiketleri döndürür.
    Herkese açıktır (Token gerekmez).
    """
    tags = crud_tag.get_all_tags(db=db, limit=limit)
    return tags
