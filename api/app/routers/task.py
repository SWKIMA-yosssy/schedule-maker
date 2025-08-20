from fastapi import APIRouter

router = APIRouter()


@router.get("/tasks")
async def list_task():
    pass


@router.post("/tasks")
async def create_task():
    pass


@router.delete("/task/{task_id}")
async def delete_task():
    pass
