from typing import Optional

from pydantic import BaseModel, Field
from datetime import datetime


class TaskBase(BaseModel):
    title: str = Field(None, example="倫理学の授業を受ける")
    start_time: datetime
    required_time: int
    user_id: int
    is_task: bool = Field(False, description="この予定がタスクかどうか")


class TaskCreate(TaskBase):
    pass


class TaskCreateResponse(TaskCreate):
    task_id: int = Field(None)

    class Config:
        orm_mode = True


class Task(TaskBase):
    task_id: Optional[int] = Field(None)

    class Config:
        orm_mode = True
