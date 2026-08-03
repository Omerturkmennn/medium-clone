import time

def test_register_user_success(client):
    """Geçerli verilerle başarılı kayıt işlemini test eder."""

    # Sahte bir POST isteği atıyoruz
    response = client.post(
        "/api/v1/users/register",
        json={
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "testpassword123"
        }
    )
    #Assert:Yazılım testlerinde ise "Bunun kesinlikle böyle olduğundan eminim, eğer değilse programı durdur ve hata ver!" demektir.
    # 1. Beklenti: İşlem başarılı olmalı ve 201 Created kodu dönmeli
    assert response.status_code == 201

    # 2. Beklenti: Dönen veriler bizim yolladıklarımızla eşleşmeli
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["username"] == "testuser"

    # 3. Beklenti: Veritabanı ona benzersiz bir ID vermiş olmalı
    assert "id" in data

    # 4. Beklenti (GÜVENLİK): Şifre (hashli olsa bile) asla dışarı dönmemeli!
    assert "password" not in data


def test_register_user_duplicate_email(client):
    """Sistemde var olan bir e-posta ile tekrar kayıt olmayı engellemeyi test eder."""

    # Önce veritabanına bir kullanıcı kaydediyoruz
    client.post(
        "/api/v1/users/register",
        json={
            "email": "test@example.com",
            "username": "test1",
            "password": "password123"
        }
    )

    # Aynı e-posta ile (fakat farklı kullanıcı adıyla) tekrar kayıt olmaya çalışıyoruz
    response = client.post(
        "/api/v1/users/register",
        json={
            "email": "test@example.com",  # AYNI E-POSTA
            "username": "test2",
            "password": "password123"
        }
    )

    # 1. Beklenti: Sistem hata vermeli ve 400 Bad Request dönmeli
    assert response.status_code == 400

    # 2. Beklenti: Hata mesajı tam olarak bizim kodda (users.py içinde) yazdığımız mesaj olmalı
    assert response.json()["detail"] == "Bu E-posta zaten kullanılıyor"

def test_login_user_success(client):
    """Geçerli bilgilerle login olma ve token alma işlemini test eder."""

    #1. test için db ye kullanıcı kaydet
    client.post(
        "/api/v1/users/register",
        json={
            "email": "logintest@example.com",
            "username": "logintest",
            "password": "strongpassword123"
        }
    )

    #2.register olan kullanıcıyı loginliyoruz
    response = client.post(
        "/api/v1/users/login",
        json={
            "email": "logintest@example.com",
            "password": "strongpassword123"
        }
    )

    #3. aşama :Beklentiler
    assert response.status_code == 200
    data = response.json()

    # Bize 3 kritik parçayı (access_token, refresh_token ve token_type) vermiş mi?
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_refresh_token_success(client):
    """Süresi dolmuş (veya dolmamış) bir access_token'ı refresh_token ile yenilemeyi test eder."""

    #1. kullanıcıyı kaydet ve login olup ilk tokenları al
    client.post(
        "/api/v1/users/register",
        json={
            "email": "refreshtest@example.com",
            "username": "refreshtest",
            "password": "strongpassword123"
        }
    )
    login_response = client.post(
        "/api/v1/users/login",
        json={
            "email": "refreshtest@example.com",
            "password": "strongpassword123"
        }
    )
    # Elimize geçen ilk refresh_token'ı saklıyoruz
    ilk_refresh_token = login_response.json()["refresh_token"]

    time.sleep(1)

    # 2. Aşama: Bu refresh token ile yeni bir access token talep ediyoruz
    refresh_response = client.post(
        "/api/v1/users/refresh",
        json={"refresh_token": ilk_refresh_token}
    )

    # 3. Aşama: Beklentiler
    assert refresh_response.status_code == 200  # İşlem başarılı olmalı
    yeni_data = refresh_response.json()

    # Sistem bize gerçekten yeni tokenler verdi mi?
    assert "access_token" in yeni_data
    assert "refresh_token" in yeni_data

    # ekstra güvenlik: Bize verilen yeni refresh token, eskisi ile aynı olmamalı
    # Çünkü biz "Refresh Token Rotation" yani her defasında anahtar yenileme mantığı kurduk
    assert yeni_data["refresh_token"] != ilk_refresh_token