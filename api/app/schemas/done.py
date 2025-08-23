from pydantic import BaseModel


class DoneResponse(BaseModel):
    task_id: int

    class Config:
        orm_mode = True
