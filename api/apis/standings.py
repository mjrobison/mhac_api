from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date

from dao import standings
from .seasons import SeasonBase
from .teams import TeamBase

router = APIRouter()

class Standings(BaseModel):
    team_id: TeamBase
    team_name: Optional[str]
    season_id: SeasonBase
    # season: SeasonBase
    wins: int
    losses: int
    games_played: int
    win_percentage: float

@router.get('/getStandings/<season_id>', response_model=Standings)
def get_standings(season_id: UUID):
    print (standings)
    return standings.get(season_id)