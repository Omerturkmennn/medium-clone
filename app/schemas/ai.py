from pydantic import BaseModel, Field
from typing import List

# Frontend'den backende gelecek olan verinin şeması
# Kullanıcıdan sadece yazdığı makalenin içeriğini alınıyor
class AIRequest(BaseModel):
    content: str=Field(...,description="Makalenin metin içeriği")

# Frontende döndürülecek yapay zeka cevabının şeması
# Gemini dan gelen yanıtı JSON olarak bu formata oturtacağız
class AIResponse(BaseModel):
    title: str = Field(..., description="Yapay zeka tarafından önerilen ilgi makale başlığı")
    tags: List[str] = Field(..., description="Yapay zeka tarafından önerilen 5 adet etiket listesi")


class AIImproveRequest(BaseModel):
    content: str = Field(..., description="İyileştirilecek seçili metin")
    mode: str = Field(..., description="İyileştirme modu (grammar, professional, friendly)")