from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date

#import logging

#logger = logging.getLogger(__name__)

# from dao import persons as players
# from .teams import TeamBase
from dao import stats

router = APIRouter()

class SeasonStats(BaseModel):
    season_id: Optional[UUID] = None
    team_id: Optional[UUID] = None


@router.get('/getStats', tags=['stats'])
def get_Stats(season_id: Optional[UUID] = None, team_id: Optional[UUID] = None):
    return stats.stats_by_season_and_team(season_id, team_id)

@router.get('/getSeasonStats', tags=['stats'])
def get_Stats(season_stats: SeasonStats):
    print(season_stats.season_id, season_stats.team_id)
    try:
        return stats.stats_by_season_and_team(season_stats.season_id, season_stats.team_id)
    except Exception as exc:
       print(season_stats.season_id, season_stats.team_id)
       raise
