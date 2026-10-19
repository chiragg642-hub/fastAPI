from sqlmodel import create_engine, Session
from .config import settings

DATABASE_URL = "postgresql+psycopg://{settings.database_username}:{settings.database_password}@{settings.database_host}:{settings.database_port}/{settings.database_name}".format(settings=settings)

engine = create_engine(DATABASE_URL)


def get_db():
    with Session(engine) as session:
        yield session

# while True:
#     try:
        
#         conn = psycopg.connect(host=settings.database_host, dbname='fastapi', user=settings.database_username, password=settings.database_password, port=settings.database_port, row_factory=psycopg.rows.dict_row)
        
#         cur = conn.cursor()
#         print("Database connection successful")
#         break
#     except Exception as e:
#         print("Database connection failed")
#         print("Error:", e)
#         time.sleep(2)