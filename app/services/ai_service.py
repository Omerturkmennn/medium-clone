import os
import json
import urllib.request
from fastapi import HTTPException
from dotenv import load_dotenv

# .env dosyasını oku
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def generate_title_and_tags(content: str) -> dict:
    """
    Gönderilen makale içeriğini okur ve doğrudan REST API ile Gemini'dan JSON formatında başlık/etiket alır.
    Kütüphane sorunlarını atlamak için built-in urllib kullanılmıştır.
    """
    if not GEMINI_API_KEY:
        print("UYARI: GEMINI_API_KEY bulunamadı!")
        raise HTTPException(status_code=500, detail="Yapay Zeka servisi yapılandırılmamış.")

    # Google'ın Resmi REST API adresi (gemini-flash-latest modeli)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"

    prompt = f"""
    Sen profesyonel bir Medium içerik editörüsün. Aşağıdaki makale içeriğini oku ve bu makale için en uygun, ilgi çekici 1 adet başlık ve 5 adet etiket öner.
    Yazılan içeriğin dilinde yanıt ver (Türkçeyse Türkçe). Etiketler tek kelime veya çok kısa olmalı.

    Yanıtını KESİNLİKLE aşağıdaki JSON formatında, başka hiçbir açıklama veya markdown eklemeden düz metin olarak ver:
    {{
        "title": "Önerilen Başlık",
        "tags": ["etiket1", "etiket2", "etiket3", "etiket4", "etiket5"]
    }}

    Makale İçeriği:
    {content[:3000]} 
    """

    # Gemini'ın beklediği veri formatı
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    # İsteği hazırla
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        # API'ye bağlan ve yanıtı al
        with urllib.request.urlopen(req) as response:
            response_text = response.read().decode("utf-8")
            result_data = json.loads(response_text)

            # JSON içindeki gerçek metni (AI cevabını) çıkar
            ai_text = result_data["candidates"][0]["content"]["parts"][0]["text"]

            # AI markdown koymuşsa (```json) temizle
            ai_text = ai_text.replace("```json", "").replace("```", "").strip()

            # Dictionary olarak döndür (Frontend'e gidecek)
            return json.loads(ai_text)

    except Exception as e:
        print(f"AI REST API Hatası: {e}")
        raise HTTPException(status_code=500, detail="Yapay zeka yanıt üretirken bir hata oluştu.")


def generate_tldr_summary(content: str) -> dict:
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Yapay Zeka servisi yapılandırılmamış.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"
    prompt = f"""
    Aşağıdaki makale içeriğini oku ve en fazla 5 maddeden oluşan çok kısa ve öz bir 'Özet' çıkar. 
    Lütfen düz metin olarak ver, maddelerin başına veya sonuna KESİNLİKLE emoji EKLEME. Sadece sade metin kullan.

    Makale İçeriği:
    {content[:3000]}
    """
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req) as response:
            result_data = json.loads(response.read().decode("utf-8"))
            ai_text = result_data["candidates"][0]["content"]["parts"][0]["text"].strip()
            return {"tldr": ai_text}
    except Exception as e:
        print(f"AI REST API Hatası (TLDR): {e}")
        raise HTTPException(status_code=500, detail="Özet üretilirken bir hata oluştu.")


def improve_text(content: str, mode: str) -> dict:
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Yapay Zeka servisi yapılandırılmamış.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"

    # Moda göre yapay zekaya verilecek talimatı seçiyoruz
    if mode == "grammar":
        instruction = "Aşağıdaki metnin sadece dilbilgisi ve yazım hatalarını düzelt. Anlamını ve tarzını asla değiştirme."
    elif mode == "professional":
        instruction = "Aşağıdaki metni çok daha profesyonel, kurumsal ve akıcı bir iş diliyle, kaliteli bir makale dilinde yeniden yaz."
    elif mode == "friendly":
        instruction = "Aşağıdaki metni daha samimi, içten, günlük bir blog dilinde ve okuyucuyla sohbet ediyormuş gibi yeniden yaz."
    else:
        instruction = "Aşağıdaki metni düzelt ve daha akıcı hale getir."

    prompt = f"""
    Sen profesyonel bir metin editörüsün. {instruction}
    Bana SADECE düzeltilmiş/iyileştirilmiş metni ver. Ek açıklama, yorum, "İşte metniniz" veya "Tabii ki" gibi başlangıç cümleleri KESİNLİKLE kullanma. Sadece nihai metni döndür.

    İyileştirilecek Metin:
    {content}
    """

    data = {"contents": [{"parts": [{"text": prompt}]}]}
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req) as response:
            result_data = json.loads(response.read().decode("utf-8"))
            ai_text = result_data["candidates"][0]["content"]["parts"][0]["text"].strip()
            return {"improved_text": ai_text}
    except Exception as e:
        print(f"AI REST API Hatası (Improve Text): {e}")
        raise HTTPException(status_code=500, detail="Metin iyileştirilirken bir hata oluştu.")
