from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime
from sqlalchemy import Boolean
from app.db import Base


class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, autoincrement=True)
    is_task = Column(Boolean, nullable=False, default=True)#pythonでいうbool型みたいなもん
    start_time = Column(DateTime(timezone=True))
    required_time = Column(Integer)
    user_id = Column(Integer)
    title = Column(String(1024))

    done = relationship("Done", back_populates="task",
                        cascade="delete")


class Done(Base):
    __tablename__ = "dones"

    task_id = Column(Integer, ForeignKey("tasks.task_id"), primary_key=True)
    task = relationship("Task", back_populates="done")
