from fastapi import FastAPI
from app.api import api_router

app = FastAPI(
    title="Momentum Interview API",
    description="A modern FastAPI backend structured with SQLAlchemy and Alembic.",
    version="1.0.0",
)


# @app.get("/")
# async def root():
#     return {
#         "message": "Welcome to Momentum Interview API!",
#         "docs_url": "/docs",
#     }
#
#
# # Include our modular API router
# app.include_router(api_router, prefix="/api")
