from fastapi import APIRouter, Depends,HTTPException
from google.genai._gaos.resources.interactions.googlemapsresultstep import result

from app.schemas.ai import AIRequest, AIResponse, AIImproveRequest, AIArticleChatRequest, AITranslationRequest, \
    AIImagePromptRequest, AIDraftRequest, AIRequest, AIResponse, PremiumAudioRequest, AICommentAnalysisRequest
from app.services.ai_service import generate_title_and_tags, generate_tldr_summary, improve_text, chat_with_article, \
    translate_text, generate_image_prompt, generate_draft, fact_check_article, generate_premium_audio, analyze_comments

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

@router.post("/chat-with-article")
def post_chat_with_article(request: AIArticleChatRequest):
    """Makale içeriğini ve kullanıcının sorusunu alır, yapay zekanın makaleye özel cevabını döner."""
    return chat_with_article(request.content, request.user_message)

@router.post("/translate")
def post_translate(request: AITranslationRequest):
    """Metni veya HTML'i istenen dile çevirir."""
    return translate_text(request.text, request.target_lang)

@router.post("/generate-image-prompt")
def post_generate_image_prompt(request: AIImagePromptRequest):
    """Makale başlık ve içeriğine göre AI görsel istemi (prompt) üretir."""
    return generate_image_prompt(request.title, request.content)

@router.post("/generate-draft")
def post_generate_draft(request: AIDraftRequest):
    """Anahtar kelimelere göre makale taslağı üretir."""
    return generate_draft(request.keywords)


@router.post("/fact-check")
def post_fact_check(request: AIRequest):
    """Makalenin içeriğini AI ile doğrular (Fact-Check) ve sonuç döner."""
    return fact_check_article(request.content)

from fastapi import BackgroundTasks

@router.post("/text-to-speech")
def post_generate_audio(request: PremiumAudioRequest, background_tasks: BackgroundTasks):
    """Makale metnini alıp Coqui TTS ile referans sesi klonlar ve statik URL döner."""
    import os
    audio_filename = f"audio_{request.post_id}.wav"
    audio_path = os.path.join("uploads", audio_filename)
    
    # Dosya zaten hazırsa hemen URL'yi dön (Eski sistem gibi çalışır)
    if os.path.exists(audio_path):
        return {"audio_url": f"/static/{audio_filename}", "status": "ready"}
        
    # Dosya yoksa hiç bekleme yapma, arka plana at ve anında 'hazırlanıyor' mesajı dön.
    background_tasks.add_task(generate_premium_audio, request.content, request.post_id)
    return {
        "audio_url": None, 
        "status": "processing", 
        "message": "Ses dosyası şu an yapay zeka tarafından hazırlanıyor. Lütfen 5 dakika sonra tekrar deneyin."
    }

@router.post("/analyze-comments")
def post_analyze_comments(request: AICommentAnalysisRequest):
    """Makaleye ait yorumları alır ve genel duygu durumu (sentiment) özetini döner."""
    if not request.comments:
        raise HTTPException(status_code=400, detail="Analiz edilecek yorum bulunamadı.")
    return analyze_comments(request.comments)
