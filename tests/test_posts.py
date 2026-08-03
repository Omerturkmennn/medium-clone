def test_create_post_success(client):
    """Giriş yapmış bir kullanıcının yeni bir makale oluşturmasını test eder."""

    #1. aşama :sisteme yazar olarak kaydol ve giriş yap(token al)
    client.post(
        "/api/v1/users/register",
        json={
              "email": "yazar@example.com",
              "username": "yazar1",
              "password": "password123"}
    )
    login_response = client.post(
        "/api/v1/users/login",
        json={
            "email": "yazar@example.com",
            "password": "password123"
        }
    )
    access_token = login_response.json()["access_token"]

    # 2. Aşama: Token ile birlikte makale oluşturma isteği at
    response = client.post(
        "/api/v1/posts",
        json={
            "title": "Pytest ile Test Yazmak",
            "content": "Bugün FastAPI projemize harika testler yazdık..."
        },
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # 3. Aşama: Beklentiler
    assert response.status_code == 201  # 201 Created dönmeli
    data = response.json()
    assert data["title"] == "Pytest ile Test Yazmak"
    assert "id" in data  # Veritabanı makaleye bir ID vermiş olmalı


def test_create_post_unauthorized(client):
    """Giriş yapmamış birinin makale oluşturmaya çalışmasını engeller."""

    #token olmadan istek atılıyor
    response = client.post(
        "/api/v1/posts",
        json={
            "title": "Hacker Makalesi",
            "content": "Sisteme sızıp makale oluşturmaya çalışıyorum!"
        }
    )
    # Sistemin bizi 401 Unauthorized ile geri çevirmesini bekliyoruz
    assert response.status_code == 403



def test_get_all_posts(client):
    """Ana sayfadaki makalelerin (Feed) liste halinde çekilebilmesini test eder."""

    # Önce ana sayfaya GET isteği atıyoruz
    response = client.get("/api/v1/posts/")

    # İşlem başarılı olmalı ve bize bir liste (array) dönmeli
    assert response.status_code == 200
    assert isinstance(response.json(), list)