from fastapi import APIRouter

from .teams_api import router as teams

api_router = APIRouter()

root_path = '/'
api_router.include_router(teams, tags=['admin'])