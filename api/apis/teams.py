from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date

from dao import teams


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

class TeamUpdate(TeamBase):
    team_id: UUID

class SeasonTeam(BaseModel):
    team_id: UUID
    season_id: UUID

class SeasonTeamOut(SeasonTeam):
    season_team_id: UUID

@router.get('/getTeams', response_model=List[TeamOut], summary="Get All Teams", tags=['teams'])
async def get():
    return teams.get_list()

@router.get('/getTeams/{slug}', response_model=List[TeamOut], summary="Get an invididual team", tags=['teams'])
def getTeam(slug):
    return teams.get(slug)

@router.get('/getSeasonTeams/{slug}', response_model=List[TeamOut], summary="Get an invididual team", tags=['teams'])
def getSeasonTeams(slug):
    return teams.get(slug)

@router.post('/addTeamToSeason', tags=['teams', 'seasons'])
async def add_to_season(season_team: SeasonTeam):
    return teams.add_to_season(season_team)

@router.post('/createTeam', tags=['teams'])
async def create_team(team: TeamBase):
    return teams.create(team)
