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


def chat_with_article(content: str, user_message: str) -> dict:
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Yapay Zeka servisi yapılandırılmamış.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"

    prompt = f"""
    Sen, aşağıdaki makalenin yazarı tarafından görevlendirilmiş, okuyuculara yardımcı olan akıllı ve kibar bir yapay zeka asistanısın.
    Görevlerin:
    - Kullanıcının sorusuna SADECE aşağıdaki makale içeriğine dayanarak cevap ver.
    - Eğer soru makaleyle alakasızsa (örneğin hava durumu, farklı konular vs.) kibarca "Üzgünüm, ben sadece bu makale içeriği hakkında soruları yanıtlamak için buradayım." de.
    - Kısa, net, anlaşılır ve bir chat ekranına uygun samimi bir dille cevap ver. (Maksimum 3-4 cümle kullan).

    --- MAKALE İÇERİĞİ ---
    {content}
    ----------------------

    Kullanıcının Sorusu: {user_message}
    Sadece cevabı yaz:
    """

    data = {"contents": [{"parts": [{"text": prompt}]}]}
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req) as response:
            result_data = json.loads(response.read().decode("utf-8"))
            ai_text = result_data["candidates"][0]["content"]["parts"][0]["text"].strip()
            return {"reply": ai_text}
    except Exception as e:
        print(f"AI REST API Hatası (Chat): {e}")
        raise HTTPException(status_code=500, detail="Sohbet asistanı şu an yanıt veremiyor.")


def translate_text(text: str, target_lang: str) -> dict:
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Yapay Zeka servisi yapılandırılmamış.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"

    language = "English" if target_lang == "en" else "Turkish"

    prompt = f"""
    Sen mükemmel bir profesyonel çevirmensin. 
    Aşağıdaki metni orijinal dilini algılayıp doğrudan {language} diline çevir.

    ÇOK ÖNEMLİ KURALLAR:
    - Metnin içinde '|||---|||' şeklinde ayırıcılar (separators) bulunuyor. Bu ayırıcıları KESİNLİKLE çevirme, silme veya yerini değiştirme! Çevrilmiş metni tam olarak aynı yerlerde bu ayırıcılarla birleştirerek geri ver.
    - Eğer içerikte HTML etiketleri (Örn: <p>, <strong> vb.) varsa KESİNLİKLE bozma. Sadece içindeki metni çevir.
    - SADECE çevrilmiş metni döndür. "İşte çeviriniz:", "Ayırıcıları korudum" gibi ekstra hiçbir açıklama ekleme.

    Çevrilecek İçerik:
    {text}
    """

    data = {"contents": [{"parts": [{"text": prompt}]}]}
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req) as response:
            result_data = json.loads(response.read().decode("utf-8"))
            ai_text = result_data["candidates"][0]["content"]["parts"][0]["text"].strip()
            if ai_text.startswith("```html") and ai_text.endswith("```"):
                ai_text = ai_text[7:-3].strip()
            return {"translated_text": ai_text}
    except Exception as e:
        print(f"AI REST API Hatası (Translate): {e}")
        raise HTTPException(status_code=500, detail="Metin çevrilirken bir hata oluştu veya API sınırına ulaşıldı.")

def generate_draft(keywords: str) -> dict:
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Yapay Zeka servisi yapılandırılmamış.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"

    prompt = f"""
    Sen profesyonel, okuyucuyu icine ceken ve surukleyici bir yazar / icerik ureticisisin.
    Sana asagida birkac anahtar kelime veya kisa bir konu basligi verecegim. Bu kelimeleri kullanarak zengin, anlasilir ve bilgilendirici bir SEO uyumlu makale / blog yazisi hazirla.
    Yazin basliklarla (H2, H3), paragraflarla duzenlenmis ve HTML formatinda (sadece <h2>, <h3>, <p>, <ul>, <li>, <strong>) olmalidir.
    KESINLIKLE markdown (```html vs) KULLANMA, dogrudan metin ve html etiketleri icersin. En sonuna kisa bir sonuc paragrafi ekle.

    Anahtar Kelimeler: {keywords}
    """

    data = {"contents": [{"parts": [{"text": prompt}]}]}
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req) as response:
            result_data = json.loads(response.read().decode("utf-8"))
            ai_text = result_data["candidates"][0]["content"]["parts"][0]["text"].strip()
            if ai_text.startswith("```html") and ai_text.endswith("```"):
                ai_text = ai_text[7:-3].strip()
            elif ai_text.startswith("```") and ai_text.endswith("```"):
                ai_text = ai_text[3:-3].strip()
            return {"draft": ai_text}
    except Exception as e:
        print(f"AI REST API Hatasi (Draft): {e}")
        raise HTTPException(status_code=500, detail="Makale taslagi uretilirken hata olustu.")

def generate_image_prompt(title: str, content: str) -> dict:
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Yapay Zeka servisi yapilandirilmamis.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
    Sen profesyonel bir Prompt (Gorsel Istemi) Muhendisisin.
    Sana bir makalenin basligini ve icerigini verecegim. Sen bu makaleyi en iyi temsil edecek, etkileyici, yuksek kaliteli bir dijital sanat veya fotograf icin INGILIZCE bir 'Prompt' (Gorsel cizdirme komutu) yazacaksin.
    Lutfen kisa (maks 3-4 cumle) ama betimleyici olsun. SADECE INGILIZCE PROMPT METNINI ver. Baska hicbir aciklama yapma.

    Baslik: {title}
    Icerik: {content[:1000]}
    """

    data = {"contents": [{"parts": [{"text": prompt}]}]}
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req) as response:
            result_data = json.loads(response.read().decode("utf-8"))
            ai_text = result_data["candidates"][0]["content"]["parts"][0]["text"].strip()
            return {"image_prompt": ai_text}
    except Exception as e:
        print(f"AI REST API Hatasi (Image Prompt): {e}")
        raise HTTPException(status_code=500, detail="Gorsel istemi uretilirken hata olustu.")


def fact_check_article(content: str) -> dict:
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Yapay Zeka servisi yapılandırılmamış.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"

    prompt = f"""
    Sen profesyonel ve tarafsız bir doğruluk kontrolü (Fact-Checker) uzmanısın.
    Aşağıdaki makaleyi dikkatlice oku. Makalenin içerdiği bilimsel, tarihsel, istatistiksel bilgileri veya iddiaları teyit et.
    Eğer makalede tamamen doğru, çok iyi aktarılmış bilgiler varsa bunu belirt. Eğer yanlış, eksik veya şüpheli bir bilgi varsa kibar ve yapıcı bir dille okuyucuyu uyar.
    Sonucu kısa, öz ve birkaç paragraflık akıcı bir Türkçe metin olarak ver. Sadece analiz sonucunu yaz.

    Makale İçeriği: {content[:3000]}
    """

    data = {"contents": [{"parts": [{"text": prompt}]}]}
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req) as response:
            result_data = json.loads(response.read().decode("utf-8"))
            ai_text = result_data["candidates"][0]["content"]["parts"][0]["text"].strip()
            return {"fact_check": ai_text}
    except Exception as e:
        print(f"AI REST API Hatası (Fact-Check): {e}")
        raise HTTPException(status_code=500, detail="Doğruluk kontrolü yapılırken bir hata oluştu.")
