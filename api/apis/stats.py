from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel
from uuid import UUID
from psycopg2.errors import OperationalError
from dao import stats

router = APIRouter()

class SeasonStats(BaseModel):
    season_id: Optional[UUID] = None
    team_id: Optional[UUID] = None


@router.get('/getStats')
def get_stats(season_id: Optional[UUID] = None, team_id: Optional[UUID] = None):
    try:
        statistics = stats.stats_by_season_and_team(season_id, team_id)
        if len(statistics) < 1:
            raise HTTPException(status_code=404, detail="Couldn't find stats for the season or team")
    except OperationalError as oe:
        print(str(oe))
        raise HTTPException(status_code=500, detail="there was a problem with the server.")
    return statistics

@router.get('/getSeasonStats')
def get_season_stats(season_stats: SeasonStats):
    print(season_stats.season_id, season_stats.team_id)
    try:
        statistics = stats.stats_by_season_and_team(season_stats.season_id, season_stats.team_id)
        if len(statistics) < 1:
            raise HTTPException(status_code=404, detail="Couldn't find stats for the season or team")
    except Exception as exc:
       print(season_stats.season_id, season_stats.team_id)
       raise HTTPException(status_code=500, detail="Something went wrong")
