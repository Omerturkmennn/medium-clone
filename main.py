from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from fastapi.middleware.cors import CORSMiddleware

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.rate_limit import limiter


# Yazdığım endpointleri içeren  importlar
from app.api.v1.endpoints import users,posts,comments,likes,followers,bookmarks,ws,notifications


app = FastAPI(title="Medium Clone API",
              description="API for medium clone",
              version="1.0.0",)

#CORS ayarları
# Frontend'in hangi adreslerden istek atabileceğini belirliyoruz
origins = [
    "http://localhost:3000", # React, Vue, Next.js vb. için
    "http://localhost:5173", # Vite için
    "http://127.0.0.1:5500", # VS Code Live Server için
    "*" # Dikkat: Geliştirme aşamasında kolaylık olsun diye tüm adreslere izin veriyoruz. Canlıya alırken bu satırı kaldırılmalı.
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

app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])

app.include_router(comments.router, prefix="/api/v1/comments", tags=["Comments"])

app.include_router(likes.router, prefix="/api/v1/likes", tags=["Likes"])

app.include_router(followers.router, prefix="/api/v1/followers", tags=["Followers"])

app.include_router(bookmarks.router, prefix="/bookmarks", tags=["bookmarks"])

app.include_router(ws.router, prefix="/ws", tags=["websockets"])


# API'nin ayakta olup olmadığını kontrol edebilmek için ana dizine basit bir karşılama mesajı
@app.get("/")
def root():
    """API'nin çalışıp çalışmadığını test etmek için kök dizin"""
    return {"message": "Medium Clone API'ye Hoş Geldiniz!"}