from fastapi import APIRouter

from app.api.routes import health, summarize

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(summarize.router, tags=["Summarize"])