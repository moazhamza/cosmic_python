from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.allocation.router import router as allocation_router
from src.repository.dependencies import create_db_and_tables, drop_tables


app = FastAPI()


@asynccontextmanager
async def lifecycle(_: FastAPI):
    """Lifecycle"""
    create_db_and_tables()
    yield
    drop_tables()


app.include_router(router=allocation_router)
