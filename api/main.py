from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.router import livros_router
from api.database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="API de Livros", lifespan=lifespan)
app.include_router(livros_router.router)