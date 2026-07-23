from sqlalchemy import Column, Integer, String, Text
from app.database import Base


class Playbook(Base):
    __tablename__ = "playbook"

    playbook_id      = Column(Integer, primary_key=True, autoincrement=True)
    name             = Column(String(100))
    platform         = Column(String(20))     # unix / windows / any
    trigger_keywords = Column(Text)           # comma-separated
    action_tier      = Column(Integer)        # 0 / 1 / 2 / 3
    script           = Column(Text)
    verify_command   = Column(Text)
    description      = Column(Text)
    success_count    = Column(Integer, default=0)
    failure_count    = Column(Integer, default=0)
