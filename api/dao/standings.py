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
        # 'team_id': team_get(row['team_id']),
        # 'season_id': season_get(row['season_id']),
        'team': row['team_id'],
        'team_name': row['team_name'],
        'season_id': row['season_id'],
        'wins': row['wins'],
        'losses': row['losses'],
        'games_played': row['games_played'],
        # 'games_behind': calcGamesBehind()
        'games_behind': 0,
        'win_percentage':  row['win_percentage']
    }
    return Standings

def get_a_season(id) -> Standings:
    DB = db()
    stmt = text(f'''SELECT * FROM mhac.standings
    INNER JOIN mhac.season_teams_with_names
        ON standings.season_id = season_teams_with_names.season_id
        AND standings.team_id = season_teams_with_names.id
    INNER JOIN mhac.seasons
        ON season_teams_with_names.season_id = seasons.id
    WHERE standings.season_id = :id
    ORDER BY win_percentage DESC''')
    stmt = stmt.bindparams(id=id)
    result = DB.execute(stmt)
    
    DB.close()
    standings_list = []
    for row in result:
        standings_list.append(row_mapper(row))
    return standings_list

def get(level=None) -> Standings:
    DB = db()
    where = """AND level_name = '18U Boys' """  
    if level:
        where = """AND level_name = :level """
    stmt = text(f'''SELECT * FROM mhac.standings
        INNER JOIN mhac.season_teams_with_names
            ON standings.season_id = season_teams_with_names.season_id
            AND standings.team_id = season_teams_with_names.id
        INNER JOIN mhac.seasons
            ON season_teams_with_names.season_id = seasons.id
        WHERE seasons.archive is null
        {where}
        ORDER BY win_percentage DESC''')
    result = DB.execute(stmt)
    DB.close()
    standings_list = []
    for row in result:
        standings_list.append(row_mapper(row))
    return standings_list


def add_to_standings(team_id, event, database):
    if event:
        update = text('''wins = wins + 1 ''')
    else:
        update = text('''losses = losses + 1 ''')
    
    try: 
        update = text(f'''UPDATE mhac.standings
                    SET games_played = games_played + 1, {update}
                    WHERE team_id = :team_id ''')
        
        stmt = update.bindparams(team_id = team_id)
        database.execute(stmt)

        update = text(f'''UPDATE mhac.standings
            SET win_percentage = case when wins = 0 THEN 0.00 else wins/games_played::numeric(5,4) end
            WHERE team_id = :team_id ''')
        
        stmt = update.bindparams(team_id = team_id)
        database.execute(stmt)
    except Exception as exc:
        raise exc


def remove_from_standings(team_id, event, database):
    if event:
        update = text('''wins = wins - 1 ''')
    else:
        update = text('''losses = losses - 1 ''')
    
    try: 
        update = text(f'''UPDATE mhac.standings
                    SET games_played = games_played - 1, {update}
                    WHERE team_id = :team_id ''')
        
        stmt = update.bindparams(team_id = team_id)
        database.execute(stmt)

        update = text(f'''UPDATE mhac.standings
        SET win_percentage = case when wins = 0 THEN 0.00 else wins/games_played::numeric(5,4) end
        WHERE team_id = :team_id ''')
    
        stmt = update.bindparams(team_id = team_id)
        database.execute(stmt)
    except Exception as exc:
        raise exc
  

def add_loss():
    pass

