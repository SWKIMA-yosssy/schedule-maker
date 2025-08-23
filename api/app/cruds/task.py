from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import app.models.task as task_model
import app.schemas.task as task_schema
from sqlalchemy.orm import selectinload
from datetime import date, datetime, timedelta,time

from typing import List,Tuple,Optional
from sqlalchemy.engine import Result
import calendar
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

#完了フラグも一緒に取得 task_id,is_task,start_time,required_time,deadline,user_id,title,done
async def get_tasks_with_done(db: AsyncSession) -> List[Tuple[int,bool,datetime, time,datetime,int,str,bool]]:
    result: Result = await (
        db.execute(
            select(
                task_model.Task.task_id,
                task_model.Task.is_task,
                task_model.Task.start_time,
                task_model.Task.required_time,
                task_model.Task.deadline,
                task_model.Task.user_id,
                task_model.Task.title,
                task_model.Done.task_id.isnot(None).label("done"),
            ).outerjoin(task_model.Done)
        )
    )
    return result.all()

#やっていないかつ開始時点を持たないタスクを習得

async def get_tasks_filterd(
        db: AsyncSession,
        Done:bool,
        is_task:bool
        ) -> List[Tuple[int,bool,datetime, time,datetime,int,str,bool]]:
    # Done が True の場合は done があるもの、False の場合は done がないもの
    done_filter = task_model.Done.task_id.isnot(None) if Done else task_model.Done.task_id.is_(None)

    # is_task の値に応じてフィルター
    is_task_filter = task_model.Task.is_task.is_(is_task)
    result: Result = await (
        db.execute(
            select(
                task_model.Task.task_id,
                task_model.Task.is_task,
                task_model.Task.start_time,
                task_model.Task.required_time,
                task_model.Task.deadline,
                task_model.Task.user_id,
                task_model.Task.title,
                task_model.Done.task_id.isnot(None).label("done"),
            ).outerjoin(task_model.Done)
            .where(
               done_filter,
               is_task_filter
            )
        )
    )
    return result.all()
    
#自分でdone,is_task値を選べる



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

#taskのリストを受け取って、required_timeの合計を返す
def sum_required_time(tasks):
    total = timedelta()
    for task in tasks:
        t = task.required_time
        if t:  # None でない場合
            total += timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
    return total

async def return_sumreq_by_date(
    db: AsyncSession,
    target_date: date,
) -> List[task_schema.Task]:
    # 日付範囲
    start_of_day = datetime.combine(target_date, datetime.min.time())
    end_of_day = start_of_day + timedelta(days=1)
    # フィルター条件
    is_task_filter = task_model.Task.is_task.is_(False)
    done_filter = task_model.Done.task_id.is_(None)

    # クエリ実行
    result = await db.execute(
        select(task_model.Task)
        .outerjoin(task_model.Done)
        .options(selectinload(task_model.Task.done))
        .where(
            task_model.Task.start_time >= start_of_day,
            task_model.Task.start_time < end_of_day,
            done_filter,
            is_task_filter
        )
    )
    return timedelta(hours=12)-sum_required_time(result.scalars().all())

async def sum_required_time_per_day_by_month(
     db:AsyncSession,
    year:int,
    month:int,
    )->List[Tuple[date,timedelta]]:
    days_in_month = calendar.monthrange(year, month)[1]#整数型でほしいためcalenderを使用

    result_list: List[Tuple[date, timedelta]] = []
    for day in range(1,days_in_month+1):
        current_date=date(year,month,day)

        total_required_time=await return_sumreq_by_date(db,current_date)
        result_list.append((current_date,total_required_time))
    return result_list

#テトリス用関数は以下に

# 締切が最も近いTodoのIDを取得
async def get_nearest_deadline_task(
    db: AsyncSession, target_date: datetime
) -> Optional[int]:
    is_task_filter = task_model.Task.is_task.is_not(False)
    result = await db.execute(
        select(task_model.Task)
        .where(
               task_model.Task.deadline >= target_date,#今日以降
               is_task_filter#Todoである
               )  
        .order_by(task_model.Task.deadline.asc())        # 締切の早い順
        .limit(1)                                        # 先頭1件
    )
    task = result.scalar_one_or_none()
    return task.task_id if task else None

#最も直近の予定のIDを取得