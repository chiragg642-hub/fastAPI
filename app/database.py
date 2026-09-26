from sqlmodel import create_engine, Session

DATABASE_URL = "postgresql+psycopg://postgres:123456@localhost:5432/fastapi"

engine = create_engine(DATABASE_URL)


def get_db():
    with Session(engine) as session:
        yield session