from typing import List
from datetime import datetime, date
from fastapi import APIRouter, Depends, Path

from sqlalchemy.ext.asyncio import AsyncSession


import app.cruds.task as task_crud

from app.db import get_db
import app.schemas.task as task_schema

router = APIRouter()


@router.get("/calendars/{month}")
async def list_busyness_of_month(
    year: int = Path(..., ge=2000, le=2100),
    month: int = Path(..., ge=1, le=12),
    db: AsyncSession = Depends(get_db)
):
    pass
