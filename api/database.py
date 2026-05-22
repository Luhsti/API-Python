from sqlmodel import SQLModel, create_engine, Session
from api.models import Livro

DATABASE_URL = "postgresql://postgres:admin@localhost:32768/postgres"

engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session