from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.router import livros_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title="API de Livros", lifespan=lifespan)
app.include_router(livros_router.router)