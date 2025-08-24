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

async def update_task(
    db: AsyncSession,
    original: task_model.Task,
    updated_data: dict
) -> task_model.Task:
    for key, value in updated_data.items():
        setattr(original, key, value)
    db.add(original)
    await db.commit()
    await db.refresh(original)
    return original


# 指定したIDのタスクを取得
async def get_task(db: AsyncSession, task_id: int) -> Optional[task_model.Task]:
    result: Result = await db.execute(
        select(task_model.Task).filter(task_model.Task.task_id == task_id)
    )
    task: Optional[Tuple[task_model.Task]] = result.first()
    return task[0] if task is not None else None  # 要素が一つであってもtupleで返却されるので１つ目の要素を取り出す

#完了フラグも一緒に取得 task_id,is_task,start_time,required_time,deadline,user_id,title,done
async def get_tasks_with_done(db: AsyncSession) -> List[Tuple[int,bool,datetime, time,datetime,int,str,bool,bool]]:
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
                task_model.Task.tetrisd
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

# 締切が最も近いtetrisされていないTodoのIDを取得
async def get_nearest_deadline_task(
    db: AsyncSession, target_date: datetime
) -> Optional[int]:
    is_task_filter = task_model.Task.is_task.is_(True)
    done_filter = task_model.Done.task_id.is_(None)
    tetrisd_filter=task_model.Task.tetrisd.is_(False)
    result = await db.execute(
        select(task_model.Task)
        .outerjoin(task_model.Done)
        .where(
               task_model.Task.deadline >= target_date,#今日以降
               is_task_filter,#Todoである
                done_filter,#完了していない
                tetrisd_filter#まだtetrisされていない
               )  
        .order_by(task_model.Task.deadline.asc())        # 締切の早い順
        .limit(1)                                        # 先頭1件
    )
    task = result.scalar_one_or_none()
    return task.task_id if task else None

#最も直近(開始時点が近い)予定のIDを取得
async def get_nearest_starttime_task(
    db: AsyncSession, target_date: datetime
) -> Optional[int]:
    is_task_filter = task_model.Task.is_task.is_(False)
    done_filter = task_model.Done.task_id.is_(None)
    result = await db.execute(
        select(task_model.Task)
        .outerjoin(task_model.Done)
        .where(
               task_model.Task.start_time >= target_date,#今日以降
               is_task_filter,#予定(Todoでない)
               done_filter#完了していない
               )  
        .order_by(task_model.Task.start_time.asc())        # starttimeの早い順
        .limit(1)                                        # 先頭1件
    )
    task = result.scalar_one_or_none()
    return task.task_id if task else None

#最も直近(終了時点が近い)予定のIDを取得
async def get_nearest_endtime_task(
    db: AsyncSession, target_date: datetime
) -> Optional[int]:
    is_task_filter = task_model.Task.is_task.is_(False)
    done_filter = task_model.Done.task_id.is_(None)
    result = await db.execute(
        select(task_model.Task)
        .outerjoin(task_model.Done)
        .where(
               task_model.Task.start_time >= target_date,#今日以降
               is_task_filter,#予定(Todoでない)
               done_filter#完了していない
               )  
        .order_by(task_model.Task.deadline.asc())        # endtimeの早い順
        .limit(1)                                        # 先頭1件
    )
    task = result.scalar_one_or_none()
    return task.task_id if task else None


#task_is=falseの予定についてdeadlineをstart_timeとrequired_timeから計算し上書きする
async def update_deadline_for_schedules(db: AsyncSession) -> None:
    """
    is_task=False のタスクについて、deadlineを start_time + required_time で上書き
    """
    result = await db.execute(
        select(task_model.Task)
        .where(task_model.Task.is_task.is_(False))
    )
    tasks = result.scalars().all()

    for task in tasks:
        if task.start_time and task.required_time:
            # required_time は time型なので timedelta に変換
            req_delta = time_to_timedelta(task.required_time)
            task.deadline = task.start_time + req_delta
            db.add(task)  # 更新対象としてマーク
    await db.commit()

#timedeltaをtime型に変換
def timedelta_to_time(td: timedelta) -> time:
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    hours = hours % 24  # 24時間以上の分は切り捨て
    return time(hour=hours, minute=minutes, second=seconds)
#time型をtimedeltaに変換
def time_to_timedelta(t: time) -> timedelta:
    """time型をtimedeltaに変換する"""
    return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond)


# 本番のテトリス関数
async def tetris(
    db: AsyncSession,
    current_time: datetime  # どこから予定テトリスを始めるか
) -> Optional[int]:
    # 最も締め切りの近いTodoを取得
    todo_id = await get_nearest_deadline_task(db, current_time)
    # 最も開始時点の近い予定を取得
    schedule_id = await get_nearest_starttime_task(db, current_time)

    # todoが無ければ終了
    if todo_id is None:
        return schedule_id

    # Todoの情報を取得
    todo_task = await get_task(db, todo_id)
    t= todo_task.required_time  # timedelta型を推奨！
    reqtime = time_to_timedelta(t)
    # 次の予定が無いなら → そのままTodoをスケジュール化
    if schedule_id is None:
        new_schedule = task_schema.TaskCreate(
            is_task=False,
            start_time=current_time,
            required_time=timedelta_to_time(reqtime),
            deadline=None,
            user_id=todo_task.user_id,
            title=todo_task.title,
            tetrisd=True
        )
        await create_task(db, new_schedule)
        return None  # 再帰不要

    # scheduleの情報を取得
    schedule_task = await get_task(db, schedule_id)
    starttime: datetime = schedule_task.start_time#次の予定が始まる時間

    # 空き時間を計算
    free_time = starttime - current_time
    
    if schedule_task.start_time <= current_time < schedule_task.start_time + time_to_timedelta(schedule_task.required_time):
        # current_time を既存予定の終了時刻に進める
        current_time = current_time+current_time- time_to_timedelta(schedule_task.required_time)
        print("特殊ケースに入ったよ")
        # 次のスケジュールを再取得
        return await tetris(db, current_time)

    # 空き時間 >= 必要時間 の場合
    if free_time >= reqtime:
        new_schedule = task_schema.TaskCreate(
            is_task=False,
            start_time=current_time,
            required_time=t,
            deadline=None,
            user_id=todo_task.user_id,
            title=todo_task.title,
            tetrisd=True
        )
        new_current_time = current_time + reqtime
        await create_task(db, new_schedule)

    # 空き時間 < 必要時間 の場合 → 分割
    else:
        new_schedule = task_schema.TaskCreate(
            is_task=False,
            start_time=current_time,
            required_time=timedelta_to_time(free_time),
            deadline=None,
            user_id=todo_task.user_id,
            title=todo_task.title,
        )
        new_current_time = starttime
        new_reqtime = reqtime - free_time  # 残り時間

        # timedelta を time に変換
        new_reqtime_time = timedelta_to_time(new_reqtime)

        # dict を直接渡す
        await update_task(db, todo_task, {"required_time": new_reqtime_time})


        await create_task(db, new_schedule)

    # 再帰呼び出し
    return await tetris(db, new_current_time)

