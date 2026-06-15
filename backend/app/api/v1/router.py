from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    challenges,
    dashboard,
    english,
    finance,
    reviews,
    routine,
    trail,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(challenges.router)
api_router.include_router(reviews.router)
api_router.include_router(routine.router)
api_router.include_router(trail.router)
api_router.include_router(english.router)
api_router.include_router(finance.router)
api_router.include_router(dashboard.router)
