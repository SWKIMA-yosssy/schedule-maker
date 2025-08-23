from typing import List
from datetime import datetime, date
from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession


import app.cruds.task as task_crud

from app.db import get_db
import app.schemas.task as task_schema

router = APIRouter()


@router.put("/tasks/{task_id}/done", response_model=None)
async def mark_task_as_done(task_id: int):
    return


@router.delete("/tasks/{task_id}/done", response_model=None)
async def unmark_task_as_done(task_id: int):
    return
