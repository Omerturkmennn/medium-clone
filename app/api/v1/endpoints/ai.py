from fastapi import APIRouter, Depends
from app.schemas.ai import AIRequest, AIResponse,AIImproveRequest
from app.services.ai_service import generate_title_and_tags,generate_tldr_summary,improve_text

from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/generate-metadata",response_model=AIResponse)
def get_ai_suggestions(request: AIRequest, current_user: User = Depends(get_current_user)):
    """
      Frontend'den gelen makale içeriğini alır,
      AI servisine yollar ve önerilen Başlık ile Etiketleri döndürür.
      """
    ai_result=generate_title_and_tags(request.content)

    return ai_result

@router.post("/generate-tldr")
def get_ai_tldr(request: AIRequest, current_user: User = Depends(get_current_user)):
    """Frontend'den gelen makaleyi okur ve 5 maddelik TL;DR özet döner."""
    return generate_tldr_summary(request.content)

@router.post("/improve-text")
def get_ai_improve_text(request: AIImproveRequest, current_user: User = Depends(get_current_user)):
    """Frontend'den gelen metni ve modu alır, iyileştirilmiş metni döner."""
    return improve_text(request.content, request.mode)