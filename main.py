from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os



# Yazdığım endpointleri içeren  importlar
from app.api.v1.endpoints import users,posts,comments,likes,followers,bookmarks,ws


app = FastAPI(title="Medium Clone API",
              description="API for medium clone",
              version="1.0.0",)

#Eğer 'uploads' klasörü yoksa kod patlamasın, otomatik oluştursun
os.makedirs("uploads", exist_ok=True)

#Tarayıcıdan '/static/profil.jpg' diye bir istek gelirse, git bunu 'uploads' klasöründe ara
app.mount("/static", StaticFiles(directory="uploads"), name="static")

# Yazdılan users.py dosyasındaki tüm işlemleri ana uygulamaya bağlanıyor
# prefix="/api/v1/users" sayesinde users.py içindeki /register adresi aslında
# "/api/v1/users/register" haline gelmiş oluyor
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])

app.include_router(posts.router, prefix="/api/v1/posts", tags=["Posts"])


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