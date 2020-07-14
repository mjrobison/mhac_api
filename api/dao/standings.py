from sqlalchemy import Column, String
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric

from sqlalchemy.sql import text # type: ignore
from typing import TypedDict, List, Dict, Any, Optional
from uuid import uuid4, UUID
# from sqlalchemy.dialects.postgresql import JSON, UUID
from datetime import date, timedelta, datetime
from database import db

from .seasons import Season, get as season_get
from .teams import Team, get_with_uuid as team_get

DB = db()

class Standings(TypedDict):
    team_id = Team
    season_id = Season
    wins = int
    losses = int
    games_played = int
    win_percentage = float


def row_mapper(row) -> Standings:
    Standings = {
        'team_id': team_get(row['team_id']),
        'season_id': season_get(row['season_id']),
        'wins': row['wins'],
        'losses': row['losses'],
        'games_played': row['games_played'],
        # 'games_behind': row['games_behind']
        'win_percentage':  row['win_percentage']
    }
    return Standings

def get(id) -> Standings:
    stmt = text('''SELECT * FROM mhac.standings WHERE season_id = :id''')
    stmt = stmt.bindparams(id=id)
    result = DB.execute(stmt)
    row = result.fetchone()
    # row['season_id'] = season_get(row['season_id'])
    return row_mapper(row)