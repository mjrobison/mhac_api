from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date

from dao import seasons
from .teams import TeamBase
router = APIRouter()

class SeasonBase(BaseModel):
    
    level: str
    season_name: str
    season_start_date: Optional[datetime]
    roster_submission_deadline: Optional[datetime]
    # roster_addition_deadline: Optional[date]
    tournament_start_date: Optional[datetime]
    sport: str
    year: str
    # archive: Optional[str]
    # schedule: Optional[str]
    slug: str

class SeasonOut(SeasonBase):
    season_id: UUID

class SeasonIn(SeasonBase):
    season_id: UUID

class Standings(BaseModel):
    team: TeamBase
    season: SeasonBase
    wins: int
    losses: int
    games_played: int
    win_percentage: float

@router.get('/getSeason/{id}', response_model=SeasonBase, tags=['season'])
def get_a_season(id):
    return seasons.get(id)

@router.get('/getArchivedSeasons', response_model=List[SeasonBase], tags=['season'])
def get_all_seasons():
    return seasons.get_list(active=False)

@router.get('/getSeasons', response_model=List[SeasonBase], tags=['season'])
def get_seasons():
    return seasons.get_list(active=True)

@router.post('/addSeason', tags=['season'])
def add_season(season: SeasonBase):
    return seasons.create(season)

@router.put('/updateSeason', tags=['season'])
def update_season(season: SeasonIn):
    return seasons.update(season)

@router.put('/archiveSeason/{season_id}', tags=['season'])
def archive_season(season_id: UUID):
    return seasons.archive_season(season_id)

@router.get('/getCurrentSeasons')
def get_current_season():
    return seasons.get_list(active=True)

@router.get('/getActiveYear')
def get_current_season():
    return seasons.get_active_year()
