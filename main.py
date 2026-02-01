from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.scheduler import start_scheduler, stop_scheduler
from app.db.base_class import Base
from app.db.session import engine

# Create tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the scheduler
    start_scheduler()
    yield
    # Shutdown: Stop the scheduler
    stop_scheduler()

app = FastAPI(
    title=settings.PROJECT_NAME, 
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Hello World"}
