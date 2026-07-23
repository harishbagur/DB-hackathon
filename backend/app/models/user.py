from sqlalchemy import Column, Integer, String, TIMESTAMP, func
from app.database import Base


class User(Base):
    __tablename__ = "app_user"

    user_id    = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(20), unique=True)
    full_name  = Column(String(100))
    email      = Column(String(100))
    department = Column(String(50))
    role       = Column(String(50))
    location   = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())
