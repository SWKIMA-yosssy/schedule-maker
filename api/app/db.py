# from sqlalchemy import create_engine #同期通信のときのみ必要
import asyncpg
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

ASYNC_DB_URL = "postgresql+asyncpg://postgres:password@db:5432/postgres"

async_engine = create_async_engine(ASYNC_DB_URL, echo=True)
async_session = sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
)

Base = declarative_base()


async def get_db():
    async with async_session() as session:
        yield session


# 以下の設定は同期通信のときのみ必要
'''
engine = create_engine(ASYNC_DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# DBセッションを取得する関数（FastAPIのDependsで使える）

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
