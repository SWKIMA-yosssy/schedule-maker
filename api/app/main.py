from typing import Union
from sqlalchemy import text
from sqlalchemy.orm import Session
from .db import get_db
from fastapi import FastAPI, Depends

from app.routers import task
app = FastAPI()

app.include_router(task.router)

# これらはテストコードです


@app.get("/")
def read_root():
    return {"Hello": "World"}

# これらはテストコードです


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

# これらはテストコードです


@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1")).fetchone()
    return {"result": result[0]}
