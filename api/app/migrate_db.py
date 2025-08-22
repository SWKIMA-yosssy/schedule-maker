from sqlalchemy import create_engine

from app.models.task import Base

DB_URL = "postgresql://postgres:password@db:5432/postgres"
engine = create_engine(DB_URL, echo=True)


def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    reset_database()
