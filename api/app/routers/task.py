from typing import List,Tuple,Optional
from datetime import datetime, date,time, timedelta
from fastapi import APIRouter, Depends,HTTPException,Query

from sqlalchemy.ext.asyncio import AsyncSession


import app.cruds.task as task_crud

from app.db import get_db
import app.schemas.task as task_schema


router = APIRouter()


@router.get("/tasks",response_model=List[task_schema.Task])
async def list_tasks(db: AsyncSession = Depends(get_db)):
    return await task_crud.get_tasks_with_done(db)

@router.get("/tasks/filterd", response_model=List[task_schema.Task])
async def list_tasks_filterd(
    db: AsyncSession = Depends(get_db),
    done: bool = Query(True, description="完了済みならTrue"),
    is_task: bool = Query(True, description="タスクならTrue")
):
    return await task_crud.get_tasks_filterd(db, Done=done, is_task=is_task)

@router.get("/tasks/day/sumreq",response_model=timedelta)
async def sum_required_time_tasks(date:date,db: AsyncSession = Depends(get_db)):
    return await task_crud.return_sumreq_by_date(db,date)

@router.get("/tasks/month/sumreq",response_model=List[Tuple[date,timedelta]])
async def sum_required_time_tasks_month(
        year:int,
        month:int,
        db: AsyncSession = Depends(get_db)
):
    return await task_crud.sum_required_time_per_day_by_month(db,year,month)


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


#テトリス用関数は以下に
@router.get("/tasks/nearest/{target_date}", response_model=Optional[int])
async def get_nearest_task(
    date: datetime, db: AsyncSession = Depends(get_db)
):
    return await task_crud.get_nearest_deadline_task(db,date)
