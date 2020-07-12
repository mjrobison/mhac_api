from fastapi import APIRouter

from .teams import router as teams
from .players import router as players
from .seasons import router as seasons


api_router = APIRouter()

root_path = '/'
api_router.include_router(teams)
api_router.include_router(players)
api_router.include_router(seasons)