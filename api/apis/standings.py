from fastapi import APIRouter, HTTPException, status
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date

from dao import standings
from .seasons import SeasonBase
from .teams import TeamBase

router = APIRouter()

class Standings(BaseModel):
    team: UUID
    team_name: Optional[str]
    season_id: UUID
    # season: SeasonBase
    wins: int
    losses: int
    games_played: int
    games_behind: float
    win_percentage: float

@router.get('/getStandings', response_model=List[Standings])
def get_standings():
    return standings.get()

@router.get('/getStandings/{season_id}', response_model=List[Standings])
def get_season_standings(season_id: UUID):
    return standings.get_a_season(season_id)

@router.get('/lookupTeamByStandings/{season_id}/{rank}')
def get_team_from_rank(season_id: UUID, rank:int):
    team = standings.get_team_from_rank(season_id, rank)
    if not team:
        raise HTTPException(status_code=404, detail="No Team Found")
    return team

@router.post('/updateSeasonStandings', status_code=201, tags=['standings'])
def update_season_standings(season_id: UUID):
    try:
        standings.update_standings_rank(season_id)
        return 'Succesfully Updated'
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post('/updateActiveSeasonStandings', status_code=201, tags=['standings'])
def update_season_standings():
    try:
        standings.update_all_active_seasons()
        return 'Succesfully Updated'
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post('/updateTeamStandingsRank', status_code=201, tags=['standings'])
def update_team_standing_rank(team_id: UUID, rank: int):
    try:
        standings.force_standings_rank(team_id=team_id, rank=rank)
        return 'Succesfully Updated'
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
