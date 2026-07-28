from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash


def get_user_by_email(db: Session, email: str) -> User | None:
    """Veritabanından email adresine göre kullanıcı arar."""
    return db.scalar(select(User).where(User.email == email))


def get_user_by_username(db: Session, username: str) -> User | None:
    """Veritabanından kullanıcı adına göre kullanıcı arar."""
    return db.scalar(select(User).where(User.username == username))

def get_user_by_id(db: Session, user_id: str) -> User | None:
    """Veritabanından ID'ye göre kullanıcı arar."""
    return db.scalar(select(User).where(User.id == user_id))


def create_user(db: Session, user_in: UserCreate) -> User:
    """Yazılan bcrypt fonksiyonunu kullanarak şifreyi hashler ve veritabanına kaydeder."""

    # Doğrudan  get_password_hash fonksiyonun çalışıyor
    hashed_password = get_password_hash(user_in.password)

    db_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hashed_password,
        bio=user_in.bio
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user