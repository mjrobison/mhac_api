from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date

from dao import seasons

router = APIRouter()

class SeasonBase(BaseModel):
    
    season_name: str
    year: str
    level: int
    sport: int
    start_date: Optional[date]
    roster_submission_deadline: Optional[date]
    roster_addition_deadline: Optional[date]
    tournament_start_date: Optional[date]
    archive: Optional[str]
    schedule: Optional[str]

class SeasonOut(SeasonBase):
    season_id: UUID

class SeasonIn(SeasonBase):
    season_id: UUID

@router.get('/getSeason/<id>', response_model=SeasonBase)
def get_a_season(id):
    return seasons.get(id)

@router.get('/getArchivedSeasons', response_model=List[SeasonBase])
def get_all_seasons():
    return seasons.get_list(active=False)

@router.get('/getSeasons', response_model=List[SeasonBase])
def get_seasons():
    return seasons.get_list(active=True)

@router.post('/addSeason')
def add_season(season: SeasonBase):
    return seasons.create(season)

@router.put('/updateSeason')
def update_season():
    pass

@router.put('/archiveSeason/<season_id>')
def archive_season(season_id):
    pass