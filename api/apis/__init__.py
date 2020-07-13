from fastapi import APIRouter

from .teams import router as teams
from .players import router as players
from .seasons import router as seasons
from .sports import router as sports
from .games import router as games
from .standings import router as standings

api_router = APIRouter()

root_path = '/'
api_router.include_router(teams)
api_router.include_router(players)
api_router.include_router(seasons)
api_router.include_router(sports)
api_router.include_router(games)
api_router.include_router(standings)