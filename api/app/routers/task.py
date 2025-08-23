from typing import List
from datetime import datetime, date
from fastapi import APIRouter, Depends,HTTPException

from sqlalchemy.ext.asyncio import AsyncSession


import app.cruds.task as task_crud

from app.db import get_db
import app.schemas.task as task_schema

router = APIRouter()


@router.get("/tasks",response_model=List[task_schema.Task])
async def list_tasks(db: AsyncSession = Depends(get_db)):
    return await task_crud.get_tasks_with_done(db)

@router.get("/tasks/nodone&istask",response_model=List[task_schema.Task])
async def list_tasks_nodone_istask(db: AsyncSession = Depends(get_db)):
    return await task_crud.get_tasks_nodone_istask(db)

@router.post("/tasks", response_model=task_schema.TaskCreateResponse)
async def create_task(
    task_body: task_schema.TaskCreate, db: AsyncSession = Depends(get_db)
):
    return await task_crud.create_task(db, task_body)
#なぜかtureを受け付けない1で入れないとだめ

@router.get("/tasks/day/{date}", response_model=list[task_schema.Task])
async def list_tasks_by_date(
        date: date, db: AsyncSession = Depends(get_db)
):
    return await task_crud.get_tasks_by_date(db, date)


@router.get("/tasks/month/{date}", response_model=list[task_schema.Task])
async def list_tasks_by_month(
        year: int, month: int, db: AsyncSession = Depends(get_db)):
    return await task_crud.get_tasks_by_month(db, year, month)


@router.delete("/tasks/{task_id}", response_model=None)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await task_crud.get_task(db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return await task_crud.delete_task(db, original=task)
