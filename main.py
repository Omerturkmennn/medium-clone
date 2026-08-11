from fastapi import FastAPI,Request,status
from fastapi.staticfiles import StaticFiles
import os
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import Base,engine

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.rate_limit import limiter

from app.api.v1.endpoints import ai

from fastapi.responses import JSONResponse
import traceback
from app.core.logger import logger

# Yazdığım endpointleri içeren  importlar
from app.api.v1.endpoints import users,posts,comments,likes,followers,bookmarks,ws,notifications,tags

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Medium Clone API",
              description="API for medium clone",
              version="1.0.0",)

#CORS ayarları
# Frontend'in hangi adreslerden istek atabileceğini belirliyoruz
origins = [
    "http://localhost:3000", # React, Vue, Next.js vb. için
    "http://localhost:5173", # Vite için
    "http://127.0.0.1:5500", # VS Code Live Server için

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # İzin verilen kaynaklar (origin)
    allow_credentials=True,      # Cookie veya Authorization başlıklarına izin ver
    allow_methods=["*"],         # GET, POST, PUT, DELETE vb. tüm HTTP metotlarına izin ver
    allow_headers=["*"],         # Gelen tüm header'lara izin ver
)


#Eğer 'uploads' klasörü yoksa kod patlamasın, otomatik oluştursun
os.makedirs("uploads", exist_ok=True)

#Tarayıcıdan '/static/profil.jpg' diye bir istek gelirse, git bunu 'uploads' klasöründe ara
app.mount("/static", StaticFiles(directory="uploads"), name="static")

#Limiter nesnesini FastAPI uygulamasına  bağlıyoruz
app.state.limiter = limiter
# Kota aşıldığında uygulamanın çökmesi yerine düzgün bir hata (429 Too Many Requests) dönmesini sağlıyoruz
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Yazdılan users.py dosyasındaki tüm işlemleri ana uygulamaya bağlanıyor
# prefix="/api/v1/users" sayesinde users.py içindeki /register adresi aslında
# "/api/v1/users/register" haline gelmiş oluyor
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])

app.include_router(posts.router, prefix="/api/v1/posts", tags=["Posts"])

app.include_router(tags.router, prefix="/api/v1/tags", tags=["Tags"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])

app.include_router(comments.router, prefix="/api/v1/comments", tags=["Comments"])

app.include_router(likes.router, prefix="/api/v1/likes", tags=["Likes"])

app.include_router(followers.router, prefix="/api/v1/followers", tags=["Followers"])

app.include_router(bookmarks.router, prefix="/api/v1/bookmarks", tags=["bookmarks"])

app.include_router(ws.router, prefix="/ws", tags=["websockets"])

app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI"])


# API'nin ayakta olup olmadığını kontrol edebilmek için ana dizine basit bir karşılama mesajı
@app.get("/")
def root():
    """API'nin çalışıp çalışmadığını test etmek için kök dizin"""
    return {"message": "Medium Clone API'ye Hoş Geldiniz!"}


# --- GLOBAL EXCEPTION HANDLER ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Uygulama genelinde yakalanmayan tüm hataları (500 Internal Server Error) burası yakalar.
    Kullanıcıya standart bir hata dönerken, arka planda hatanın tüm detaylarını (traceback) dosyaya kaydeder.
    """
    # Hatanın detaylı yolunu (traceback) al
    error_detail = traceback.format_exc()

    # Log dosyasına yaz
    logger.error(
        f"Kritik Hata! Endpoint: {request.method} {request.url}\n"
        f"Hata Mesajı: {str(exc)}\n"
        f"Detay:\n{error_detail}"
    )

    headers = {"Access-Control-Allow-Origin": "http://localhost:5173"}

    # Kullanıcıya (Frontend'e) dönülecek cevap
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Sunucu tarafında beklenmeyen bir hata oluştu. Lütfen daha sonra tekrar deneyiniz."
        },
        headers=headers
    )