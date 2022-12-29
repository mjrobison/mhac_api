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

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


#TODO: Matt Implement sorting/games behind

class Standings(TypedDict):
    team_id = Team
    season_id = Season
    wins = int
    losses = int
    games_played = int
    games_behind = float
    win_percentage = float

def row_mapper(row, leader=None) -> Standings:
    games_behind= 0.0    
    if leader:
        games_behind =calcGamesBehind(leader, row['wins'], row['losses'])
    # logger.info(games_behind)
    Standings = {
        # 'team_id': team_get(row['team_id']),
        # 'season_id': season_get(row['season_id']),
        'team': row['team_id'],
        'team_name': row['team_name'],
        'season_id': row['season_id'],
        'wins': row['wins'],
        'losses': row['losses'],
        'games_played': row['games_played'],
        'games_behind': games_behind,
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
    ORDER BY win_percentage DESC, wins desc''')
    stmt = stmt.bindparams(id=id)
    result = DB.execute(stmt)

    DB.close()
    standings_list = []
    i = 1 
    leader = {}
    for row in result:
        if i == 1: 
            leader['wins'] = row['wins']
            leader['losses'] = row['losses']
            gb = 0 

        standings_list.append(row_mapper(row, leader))
        i += 1 
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
        ORDER BY win_percentage DESC, wins desc''')
    result = DB.execute(stmt)
    standings_list = []
    i = 1 
    leader = {}
    for row in result:
        if i == 1: 
            leader['wins'] = row['wins']
            leader['losses'] = row['losses']
            gb = 0 

        standings_list.append(row_mapper(row, leader))
        i += 1 
    DB.close()
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
            SET win_percentage = case when wins = 0 THEN 0.00 else ROUND(wins/games_played::decimal, 4) end
            WHERE team_id = :team_id ''')

        stmt = update.bindparams(team_id = team_id)
        database.execute(stmt)

        query = text('''SELECT season_id FROM mhac.standings where team_id = :team_id ''')
        stmt = query.bindparams(team_id = team_id)
        season_id = database.execute(stmt).fetchone()

        update_standings_rank(season_id=season_id[0], DB=database)

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

        check = text('''SELECT * FROM mhac.standings where team_id = :team_id ''')
        stmt = check.bindparams(team_id = team_id)
        results = database.execute(stmt)
        for r in results:
            if r['games_played'] < 0 or r['wins'] < 0 or r['losses'] < 0:
                raise Exception

        update = text(f'''UPDATE mhac.standings
        SET win_percentage = case when wins = 0 THEN 0.00 else wins/games_played::decimal end
        WHERE team_id = :team_id ''')

        stmt = update.bindparams(team_id = team_id)
        database.execute(stmt)

    except Exception as exc:
        raise exc


def add_loss():
    pass


def get_team_from_rank(season_id, rank, DB=db()):
    query = text("""SELECT * FROM mhac.standings WHERE season_id = :season_id and standings_rank = :rank """)
    query = query.bindparams(season_id=season_id, rank=rank)
    results =DB.execute(query)
    team = results.fetchone()
    if team:
        return team_get(team['team_id'])
    else:
        return None

def update_all_active_seasons(DB=db()):
    query = text('''SELECT * FROM mhac.seasons WHERE archive is null''')
    results =  DB.execute(query)

    for season in results:
        update_standings_rank(season[0], DB)


def update_standings_rank(season_id, DB= db()):
    # using the season_id determine if a change needs to be made

    # if needed apply the update
    try:

        # query = text('''SELECT ROW_NUMBER() OVER (PARTITION BY season_id ORDER BY win_percentage desc), * FROM mhac.standings WHERE season_id = :season_id;''')

        query = text('''UPDATE mhac.standings                                                                                                                                       
                    SET standings_rank = rn
                    FROM (SELECT ROW_NUMBER() OVER (PARTITION BY season_id ORDER BY win_percentage desc) as rn, * FROM mhac.standings WHERE season_id = :season_id) as r
                    WHERE standings.season_id = r.season_id 
                    AND standings.team_id = r.team_id; 
                ''')
        query = query.bindparams(season_id = season_id)
        DB.execute(query)
        DB.commit()
    except Exception as exc:
        raise


def force_standings_rank(team_id, rank, DB=db()):
    # Use the team_id to get the entire rank

    try:
        query = text('''UPDATE mhac.standings                                                                                                                                       
                    SET standings_rank = :rank
                     -- FROM (SELECT ROW_NUMBER() OVER (PARTITION BY season_id ORDER BY win_percentage desc) as rn, * FROM mhac.standings WHERE season_id = '890a3d42-84d3-4600-8cf6-75ad5f8c658f') as r
                    WHERE standings.team_id = :team_id; 
                ''')
        query = query.bindparams(team_id = team_id, rank=rank)
        DB.execute(query)
        DB.commit()
    except Exception as exc:
        raise
