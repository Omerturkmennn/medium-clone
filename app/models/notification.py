import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base

class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(String, primary_key=True,index=True,default=lambda: str(uuid.uuid4()))

    #bildirimin kime ait olduğunu tut0
    user_id = Column(String, ForeignKey('users.id',ondelete='CASCADE'),nullable=False)

    #bildirim içeriği
    message=Column(String,nullable=False)

    #bildirimin okundu/okunmadı bilgisi
    is_read = Column(Boolean, default=False)

    #bildirimin oluşturulma zamanı
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    #orm ilişkisi
    user = relationship("User")