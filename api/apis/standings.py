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
    team_id: UUID
    team_name: str 
    # season: SeasonBase
    wins: int
    losses: int
    games_played: int
    win_percentage: float

@router.get('/getStandings/<team_id>', response_model=Standings)
def get_standings(team_id):
    print (standings)
    return standings.get(id)