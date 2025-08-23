from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import app.models.task as task_model
import app.schemas.task as task_schema
from sqlalchemy.orm import selectinload
from datetime import date, datetime, timedelta


async def create_task(
    db: AsyncSession, task_create: task_schema.TaskCreate
) -> task_model.Task:
    task = task_model.Task(**task_create.dict())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_tasks_by_date(
        db: AsyncSession, target_date: date) -> list[task_model.Task]:
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
