from fastapi import FastAPI
from app.api.v1.endpoints import users, posts

# Yazdığımız endpointleri içeren users dosyasını import
from app.api.v1.endpoints import users

app = FastAPI(title="Medium Clone API",
              description="API for medium clone",
              version="1.0.0",)

# Yazdılan users.py dosyasındaki tüm işlemleri ana uygulamaya bağlanıyor
# prefix="/api/v1/users" sayesinde users.py içindeki /register adresi aslında
# "/api/v1/users/register" haline gelmiş oluyor
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])

app.include_router(posts.router, prefix="/api/v1/posts", tags=["Posts"])

# API'nin ayakta olup olmadığını kontrol edebilmek için ana dizine basit bir karşılama mesajı
@app.get("/")
def root():
    """API'nin çalışıp çalışmadığını test etmek için kök dizin"""
    return {"message": "Medium Clone API'ye Hoş Geldiniz!"}