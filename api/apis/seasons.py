from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import date

from dao import seasons
from .teams import TeamBase, TeamOut
from .levels import LevelOut
router = APIRouter()


class SeasonBase(BaseModel):
    level: str
    season_name: str
    season_start_date: Optional[date]
    roster_submission_deadline: Optional[date]
    # roster_addition_deadline: Optional[date]
    tournament_start_date: Optional[date]
    sport: str
    year: str
    archive: Optional[bool]
    slug: Optional[str]


class SeasonOut(SeasonBase):
    season_id: UUID


class SeasonIn(SeasonBase):
    season_id: str


class SeasonNew(BaseModel):
    level: List[LevelOut]
    season_name: str
    season_start_date: Optional[date]
    roster_submission_deadline: Optional[date]
    tournament_start_date: Optional[date]
    sport: Optional[str]
    year: str
    archive: Optional[bool]
    slug: Optional[str]
    season_teams: Optional[List[TeamOut]]


class SeasonUpdate(BaseModel):
    season_id: UUID
    season_name: str
    season_start_date: Optional[date]
    roster_submission_deadline: Optional[date]
    tournament_start_date: Optional[date]
    sport: str
    year: str
    archive: Optional[bool]
    slug: Optional[str]
    level: LevelOut
    season_teams: Optional[List[TeamOut]]


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


@router.get('/getSeasons/{year}', response_model=List[SeasonBase], tags=['season'])
def get_seasons_by_year(year: str):
    return seasons.get_by_year(year=year)


@router.get('/getSeasons', response_model=List[SeasonOut], tags=['season'])
def get_seasons():
    return seasons.get_list()


@router.post('/addSeason', tags=['season'])
def add_season(season: SeasonNew):
    msg = []
    for level in season.level:
        msg.append(seasons.create(season, level))
    return msg

@router.put('/updateSeason', status_code=200, tags=['season'])
def update_season(seasonsUpdate: List[SeasonUpdate]):
    errors = []
    try:
        for season in seasonsUpdate:
            # print(season)
            seasons.update(season)
    except Exception as exc:
        print(str(exc))
        errors.append(str(exc))

    if len(errors) > 0:
        raise HTTPException(status_code=500, detail="Something Went Wrong")
    return None



@router.put('/archiveSeason/{season_id}', tags=['season'])
def archive_season(season_id: UUID):
    return seasons.archive_season(season_id)


@router.get('/getCurrentSeasons', tags=['season'])
def get_current_season():
    return seasons.get_list(active=True)


@router.get('/getActiveYear', tags=['season'])
def get_current_season():
    return seasons.get_active_year()


@router.get('/getYears', tags=['season'])
def get_all_years():
    return seasons.get_all_years()


@router.get('/getAdminSeasons', tags=['season'])
def get_admin_seasons():
    return seasons.get_admin_season()