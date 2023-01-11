from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date

from dao import teams
from .addresses import Address
from psycopg2.errors import ForeignKeyViolation

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
    team = teams.get(slug=slug)
    if not team:
        raise HTTPException(status_code=404, detail="No team found")
    

@router.get('/getTeams', response_model=List[TeamOut], summary="Get All Teams", tags=['teams'])
async def get():
    teamsList =  teams.get_list()
    if len(teamsList) < 1:
        raise HTTPException(status_code=404, detail="Team or Season didn't exist")
    
    return teamsList


@router.get('/getSeasonTeams/', response_model=List[SeasonTeamOut2], summary="Get all teams for the current season",
            tags=['teams'])
@router.get('/getSeasonTeams/{slug}', response_model=List[SeasonTeamOut2], summary="Get an invididual team",
            tags=['teams'])
def getSeasonTeams(slug= None):
    return teams.get_season_teams(slug)
    

@router.get('/getSeasonTeams/{slug}/{seasonid}', response_model=SeasonTeamOut2, summary="Get an invididual team",
            tags=['teams'])
def getSeasonTeams(slug, seasonid):
    teamsList = teams.get_season_team(slug, seasonid)
    if len(teamsList) < 1:
        raise HTTPException(status_code=404, detail="Team or Season didn't exist")
    return teamsList


@router.post('/addTeamToSeason', tags=['teams', 'season'])
def add_to_season(season_team: SeasonTeam):
    try:
        teams.add_to_season(season_team)
    except ForeignKeyViolation as exc:
        raise HTTPException(status_code=404, detail="Item not found")
    return {200: 'Success'}


@router.post('/createTeam', tags=['teams'])
def create_team(team: TeamIn):
    results = teams.create(team)
    return results


@router.get('/getTeamCount/{season_id}', tags=['teams'])
def count_teams(season_id):
    return teams.get_team_count(season_id=season_id)
