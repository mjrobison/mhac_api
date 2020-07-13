from sqlalchemy import Column, String
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric

from sqlalchemy.sql import text # type: ignore
from typing import TypedDict, List, Dict, Any, Optional
from uuid import uuid4, UUID
# from sqlalchemy.dialects.postgresql import JSON, UUID
from datetime import date, timedelta, datetime
from database import db

DB = db()

class Standings(TypedDict):
    team_id = UUID
    season_id = UUID
    wins = int
    losses = int
    games_played = int
    win_percentage = float


def row_mapper(row) -> Standings:
    Standings = {
        'team_id': row['team_id'],
        'team_name': row['team_name'],
        'wins': row['wins'],
        'losses': row['losses'],
        'game_played': row['games_played'],
        'games_behind': row['games_behind']
    }

def get(id) -> Standings:
    stmt = text('''SELECT * FROM mhac.standings inner join mhac.season_teams_with_names on standings.team_id = season_teams_with_names.season_team_id WHERE standings.team_id = :id''')
    stmt = stmt.bindparams(id)
    print(stmt)
    DB.execute(stmt)
    results = DB.fetchone()
    return row_mapper(results)