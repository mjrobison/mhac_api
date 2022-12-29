from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date

from dao import teams
from .addresses import Address

router = APIRouter()


class TeamBase(BaseModel):
    team_name: str
    team_mascot: str
    main_color: str
    secondary_color: str
    website: Optional[str]
    logo_color: str
    logo_grey: str
    slug: str


class TeamOut(TeamBase):
    team_id: UUID
    address: Optional[Address]
    season_id: Optional[UUID]
    level_name: Optional[str]
    active: bool


class TeamUpdate(TeamBase):
    team_id: UUID


class SeasonTeam(BaseModel):
    team_id: UUID
    season_id: UUID


class SeasonTeamOut(SeasonTeam):
    season_team_id: UUID
    

class SeasonTeamOut2(TeamBase):
    team_id: UUID
    season_id: Optional[UUID]
    level_name: Optional[str]
    # select_team_name: str


class TeamIn(TeamBase):
    active: bool


@router.get('/getTeams/{slug}', response_model=List[TeamOut], summary="Get an invididual team", tags=['teams'])
def getTeam(slug=None):
    if slug:
        return teams.get(slug=slug)
    else:
        return teams.get_list()


@router.get('/getTeams', response_model=List[TeamOut], summary="Get All Teams", tags=['teams'])
async def get():
    return teams.get_list()


@router.get('/getSeasonTeams/', response_model=List[SeasonTeamOut2], summary="Get all teams for the current season",
            tags=['teams'])
@router.get('/getSeasonTeams/{slug}', response_model=List[SeasonTeamOut2], summary="Get an invididual team",
            tags=['teams'])
def getSeasonTeams(slug: str = None):
    return teams.get_season_teams(slug)
    

@router.get('/getSeasonTeams/{slug}/{seasonid}', response_model=SeasonTeamOut2, summary="Get an invididual team",
            tags=['teams'])
def getSeasonTeams(slug, seasonid):
    return teams.get_season_team(slug, seasonid)


@router.post('/addTeamToSeason', tags=['teams', 'season'])
async def add_to_season(season_team: SeasonTeam):
    return teams.add_to_season(season_team)


@router.post('/createTeam', tags=['teams'])
def create_team(team: TeamIn):
    results = teams.create(team)
    return results


@router.get('/getTeamCount/{season_id}', tags=['teams'])
def count_teams(season_id):
    return teams.get_team_count(season_id=season_id)
