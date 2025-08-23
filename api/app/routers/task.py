from typing import List
from datetime import datetime, date
from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession


import app.cruds.task as task_crud

from app.db import get_db
import app.schemas.task as task_schema

router = APIRouter()


@router.get("/tasks")
async def list_task():
    return [task_schema.Task(id=1,
                             title="1つ目のタスク",
                             start_time=datetime.now(),
                             required_time=30,
                             user_id=1,
                             is_task=True)]


@router.post("/tasks", response_model=task_schema.TaskCreateResponse)
async def create_task(
    task_body: task_schema.TaskCreate, db: AsyncSession = Depends(get_db)
):
    return await task_crud.create_task(db, task_body)


@router.get("/tasks/day/{date}", response_model=list[task_schema.Task])
async def list_tasks_by_date(
        date: date, db: AsyncSession = Depends(get_db)
):
    return await task_crud.get_tasks_by_date(db, date)

@router.get("/tasks/month/{date}", response_model=list[task_schema.Task])
async def list_tasks_by_month(
        year:int,month:int, db: AsyncSession = Depends(get_db)
):
    return await task_crud.get_tasks_by_month(db, year,month)

@router.delete("/task/{task_id}")
async def delete_task():
    pass
