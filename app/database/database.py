from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

#db motoru
engine = create_engine(settings.DATABASE_URL)

#db iletişimi için session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#tüm veritabanı tablolarımı bu base sınıfından türetilecek
Base = declarative_base()