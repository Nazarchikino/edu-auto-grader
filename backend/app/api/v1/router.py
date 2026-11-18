from fastapi import APIRouter

from app.api.v1 import auth, courses, practicals, submissions

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(courses.router)
api_router.include_router(practicals.router)
api_router.include_router(submissions.router)
