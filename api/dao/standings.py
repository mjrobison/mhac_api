from sqlalchemy import Column, String
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric

from sqlalchemy.sql import text # type: ignore
from typing import TypedDict, List, Dict, Any, Optional
from uuid import uuid4, UUID
# from sqlalchemy.dialects.postgresql import JSON, UUID
from datetime import date, timedelta, datetime
from database import db

from .seasons import Season, get as season_get, get_list
from .teams import Team, get_with_uuid as team_get
from .utils import calcGamesBehind

DB = db()

#TODO: Matt Implement sorting/games behind

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
        # 'games_behind': calcGamesBehind()
        'win_percentage':  row['win_percentage']
    }
    return Standings

def get_a_season(id) -> Standings:
    stmt = text('''SELECT * FROM mhac.standings WHERE season_id = :id''')
    stmt = stmt.bindparams(id=id)
    result = DB.execute(stmt)
    row = result.fetchone()
    # row['season_id'] = season_get(row['season_id'])
    return row_mapper(row)

def get(id) -> Standings:
    seasons = get_list(active=True)    
    stmt = text('''SELECT * FROM mhac.standings WHERE season_id = :id''')
    stmt = stmt.bindparams(id=id)
    result = DB.execute(stmt)
    row = result.fetchone()
    # row['season_id'] = season_get(row['season_id'])
    return row_mapper(row)

def add_to_standings(team_id, event, database):
    if event == 'win':
        update = text('''wins = wins + 1 ''')
    else:
        update = text('''losses = losses + 1 ''')
    
    update = text('''UPDATE mhac.standings
                   SET games_played = games_played + 1, {update}
                   WHERE team_id = :team_id ''')
    
    stmt = update.binparams(team_id = team_id)
    database.execute(stmt)

def remove_from_standings(team_id, event, database):
    if event:
        update = text('''wins = wins - 1 ''')
    else:
        update = text('''losses = losses - 1 ''')
    
    update = text('''UPDATE mhac.standings
                   SET games_played = games_played - 1, {update}
                   WHERE team_id = :team_id ''')
    
    stmt = update.binparams(team_id = team_id)
    database.execute(stmt)


    
    
    

def add_loss():
    pass