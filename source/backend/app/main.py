from fastapi import FastAPI

from app.api import api_router

app = FastAPI(
    title="Library API",
    description="A modern FastAPI backend structured with SQLAlchemy and Alembic.",
    version="1.0.0",
)


# Include our modular API router
app.include_router(api_router, prefix="/api")
