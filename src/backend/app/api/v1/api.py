"""
API Router configuration
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, projects, users, media

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(media.router, prefix="/media", tags=["media"])
