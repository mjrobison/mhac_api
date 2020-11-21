from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date

# from dao import persons as players
# from .teams import TeamBase
from dao import stats

router = APIRouter()

@router.get('/getStats')
def get_Stats(season_id: Optional[UUID] = None, team_id: Optional[UUID] = None):
    return stats.stats_by_season_and_team(season_id, team_id) 