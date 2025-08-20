from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:password@db:5432/postgres"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# DBセッションを取得する関数（FastAPIのDependsで使える）


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
