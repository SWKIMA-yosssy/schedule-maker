from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import app.models.task as task_model
import app.schemas.task as task_schema
from sqlalchemy.orm import selectinload
from datetime import date, datetime, timedelta

from typing import List,Tuple,Optional
from sqlalchemy.engine import Result

async def create_task(
    db: AsyncSession, task_create: task_schema.TaskCreate
) -> task_model.Task:
    task = task_model.Task(**task_create.dict())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

# 指定したIDのタスクを取得
async def get_task(db: AsyncSession, task_id: int) -> Optional[task_model.Task]:
    result: Result = await db.execute(
        select(task_model.Task).filter(task_model.Task.task_id == task_id)
    )
    task: Optional[Tuple[task_model.Task]] = result.first()
    return task[0] if task is not None else None  # 要素が一つであってもtupleで返却されるので１つ目の要素を取り出す

#完了フラグも一緒に取得 task_id,is_task,start_time,required_time,user_id,title,done
async def get_tasks_with_done(db: AsyncSession) -> List[Tuple[int,int,datetime, int,int,str,bool]]:
    result: Result = await (
        db.execute(
            select(
                task_model.Task.task_id,
                task_model.Task.is_task,
                task_model.Task.start_time,
                task_model.Task.required_time,
                task_model.Task.user_id,
                task_model.Task.title,
                task_model.Done.task_id.isnot(None).label("done"),
            ).outerjoin(task_model.Done)
        )
    )
    return result.all()

#やっていないかつ開始時点を持たないタスクを習得

async def get_tasks_nodone_istask(db: AsyncSession) -> List[Tuple[int,int,datetime, int,int,str,bool]]:
    result: Result = await (
        db.execute(
            select(
                task_model.Task.task_id,
                task_model.Task.is_task,
                task_model.Task.start_time,
                task_model.Task.required_time,
                task_model.Task.user_id,
                task_model.Task.title,
                task_model.Done.task_id.isnot(None).label("done"),
            ).outerjoin(task_model.Done)
            .where(
                task_model.Done.task_id.is_(None),
                task_model.Task.is_task==1,
            )
        )
    )
    return result.all()
    


async def get_tasks_by_date(
        db: AsyncSession, target_date: date) -> list[task_schema.Task]:
    start_of_day = datetime.combine(target_date, datetime.min.time())
    end_of_day = start_of_day + timedelta(days=1)
    result = await db.execute(
        select(
            task_model.Task
        )
        .options(selectinload(task_model.Task.done))
        .where(
            task_model.Task.start_time >= start_of_day,
            task_model.Task.start_time < end_of_day
        )
    )

    return result.scalars().all()

# 日付からその月の初日と次の月の初日を返す


def get_month_range(year: int, month: int):
    # 月の初日
    start_of_month = datetime(year, month, 1)
    # 次の月の初日
    if month == 12:  # 12月の場合は年を繰り上げ
        next_month = datetime(year + 1, 1, 1)
    else:  # それ以外は月を繰り上げ
        next_month = datetime(year, month + 1, 1)

    return start_of_month, next_month


async def get_tasks_by_month(
        db: AsyncSession, year: int, month: int) -> list[task_schema.Task]:
    start_of_month, start_of_next_month = get_month_range(year, month)

    result = await db.execute(
        select(
            task_model.Task
        )
        .options(selectinload(task_model.Task.done))
        .where(
            task_model.Task.start_time >= start_of_month,
            task_model.Task.start_time < start_of_next_month
        )
    )

    return result.scalars().all()


async def delete_task(db:AsyncSession,original:task_model.Task)->None:
    await db.delete(original)
    await db.commit()
