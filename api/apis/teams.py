from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
from uuid import UUID

from dao import teams
from .addresses import Address, AddressSeasonUpdate
from .levels import LevelBase
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


class TeamIn(TeamBase):
    team_id: UUID
    address: Optional[Address]


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
    # select_team_name: Optional[str]


class SeasonTeamUpdate(TeamBase):
    team_id: UUID
    season_id: Optional[UUID]
    address: Optional[AddressSeasonUpdate]
    level_name: Optional[str]

class SeasonTeamUpdateSeason(TeamBase):
    team_id: UUID
    season_id: Optional[UUID] = None
    address: Optional[AddressSeasonUpdate] = None

@router.get("/getTeams/{slug}", summary="Get an invididual team", tags=["teams"])
def getTeam(slug=None):
    team = teams.get(slug=slug)
    if not team:
        raise HTTPException(status_code=404, detail="No team found")
    

@router.get("/getTeams", summary="Get All Teams", tags=["teams"])
async def get():
    teamsList =  teams.get_list()
    if len(teamsList) < 1:
        raise HTTPException(status_code=404, detail="Team or Season didn't exist")
    
    return teamsList


@router.get(
    "/getSeasonTeams/", summary="Get all teams for the current season", tags=["teams"]
)
@router.get("/getSeasonTeams/{slug}", summary="Get an invididual team", tags=["teams"])
def getSeasonTeams(slug: str = None):
    return teams.get_season_teams(slug)
    

@router.get(
    "/getSeasonTeams/{slug}/{seasonid}",
    summary="Get an invididual team",
    tags=["teams"],
)
def getSeasonTeamsWithSeasonId(slug, seasonid):
    return teams.get_season_team(slug, seasonid)


@router.post("/addTeamToSeason", tags=["teams", "season"])
async def add_to_season(season_team: SeasonTeam):
    return teams.add_to_season(season_team)


@router.post("/createTeam", tags=["teams"])
async def create_team(team: TeamBase):
    return teams.create(team)


@router.get("/getTeamCount/{season_id}", tags=["teams"])
async def count_teams(season_id):
    return teams.get_team_count(season_id=season_id)
