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
    team: UUID
    team_name: Optional[str]
    season_id: UUID
    # season: SeasonBase
    wins: int
    losses: int
    games_played: int
    games_behind: int
    win_percentage: float

@router.get('/getStandings', response_model=List[Standings])
def get_standings():
    print(standings.get())
    return standings.get()

@router.get('/getStandings/{season_id}', response_model=List[Standings])
def get_standings(season_id: UUID):
    return standings.get_a_season(season_id)
