from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime
from app.db import Base


class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, autoincrement=True)
    is_task = Column(Integer)
    start_time = Column(DateTime(timezone=True))
    required_time = Column(Integer)
    user_id = Column(Integer)
    title = Column(String(1024))
