# tests/conftest.py
import pytest
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from main import app
from app.api.dependencies import get_db
from app.database.database import Base
# Gerçek veritabanını bozmamak için bir SQLite veritabanı,RAM de yaşayan
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}, #sqlite çoklu thread ile çalışması için
    poolclass=StaticPool,#bağlantı kopmasın diye
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Fastapiye gerçek db yi bırak test db yi kullan diyoruz
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

#Uygulamadaki get_db bağımlılığını (dependency) kendi uçucu veritabanımızla eziyoruz
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def test_db():
    """
    Her bir test fonksiyonu çalışmadan önce tabloları sıfırdan oluşturur.
    Test bittikten sonra (yield sonrası) tabloları tamamen siler.
    Böylece testler birbirini etkilemez, hep temiz bir veritabanı ile başlar.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    """
    Uygulamamıza sahte HTTP istekleri atabilmemizi sağlayan test tarayıcımız.
    test_db parametresi aldığı için, bu client her çağrıldığında
    önce yepyeni tertemiz bir test veritabanı ayağa kalkar.
    """
    with TestClient(app) as c:
        yield c