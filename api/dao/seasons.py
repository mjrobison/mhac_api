from sqlalchemy import Column, String
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric

from sqlalchemy.sql import text # type: ignore
from typing import TypedDict, List, Dict, Any, Optional
from uuid import uuid4, UUID
# from sqlalchemy.dialects.postgresql import JSON, UUID
from datetime import date, timedelta, datetime
from database import db

DB = db()

class Season(TypedDict):
    name                        = str
    year                        = str
    level                       = int
    sport                       = int
    start_date                  = Date
    roster_submission_deadline  = Date
    roster_addition_deadline    = Date
    tournament_start_date       = Date
    archive                     = str
    schedule                    = Optional[str]
    slug                        = str

class SeasonUpdate(Season):
    season_id                   = UUID

def row_mapper(row) -> Season:
    Season = {
        'season_id': row['season_id'],
        'level': row['level_name'],
        'season_name': row['name'],
        'season_start_date': row['start_date'],
        'roster_submission_deadline': row['roster_submission_deadline'],
        'tournament_start_date': row['tournament_start_date'],
        'sport': row['sport_name'],
        'year': row['year'],
        'slug': row['slug']

    }
    return Season

base_query = '''
SELECT seasons.id as season_id, seasons.name, seasons.start_date, seasons.roster_submission_deadline, seasons.tournament_start_date,
sports.sport_name, seasons.slug, levels.level_name, seasons.year
FROM mhac.seasons 
INNER JOIN mhac.levels 
    ON seasons.level_id = levels.id 
INNER JOIN mhac.sports 
    ON seasons.sport_id = sports.id
'''

def get_list(active=None):
    season_list = []
    where = ''
    if active:
        where = 'WHERE archive is null'
    stmt = text(f'''{base_query} {where} ''')
    result = DB.execute(stmt)
    DB.close()
    for row in result:
        season_list.append(row_mapper(row))
    return season_list

def get(slug: str):
    where = 'WHERE slug = :slug'
    stmt = text(F'''{base_query} {where} ''')
    result = DB.execute(stmt.bindparams(slug=slug))
    DB.close()
    return row_mapper(result.fetchone())

def archive_season(season: UUID):
    stmt = text(f'''UPDATE mhac.seasons
                     SET archive = True 
                     WHERE season_id = season_id ''')
    stmt = stmt.bindparams(season_id = season)
    DB = db()   
    DB.execute(stmt)
    DB.commit()
    DB.close()
    return {200: "Season Archived"}

def update(season: Season):
    stmt =text('''UPDATE mhac.seasons
                  SET name = :name, year = :year, level_id= :level_id, sport_id= :sport_id, start_date= :start_date, roster_submission_deadline= :roster_submission_deadline, tournament_start_date= :tournament_start_date 
                   WHERE season_id = :season_id ''')
    stmt = stmt.bindparams(name = season.name, year =season.year, level_id = season.level_id, sport_id = seaon.sport_id, start_date = season.start_date, roster_submission_deadline = season.roster_submission_deadline, tournament_start_date = season.tournament_start_date)
    DB = db()
    DB.execute(stmt)
    DB.commit()
    DB.close()
    return {200 : "Season Updated"}

def create(season: Season):
    DB = db()
    new_season_id= uuid4()
    stmt = text('''INSERT INTO mhac.seasons(id, name, year, level_id, sport_id, start_date, roster_submission_deadline, tournament_start_date, archive) 
                VALUES
                (:id, :name, :year, :level, :sport, :start_date, :roster_submission_deadline, :tournament_start_date, :archive )''')
    DB.execute(stmt.bindparams(id= new_season_id, name= season.season_name, year = season.year, level = season.level, sport = season.sport, start_date =season.start_date , roster_submission_deadline= season.roster_submission_deadline, tournament_start_date = season.tournament_start_date, archive = None))
    DB.commit()
    DB.close()
    return {200: f'{new_season_id} Added '}

def get_active_year(archive=None):
    DB = db()
    stmt = text ('''
        SELECT DISTINCT name, year FROM mhac.seasons
        WHERE archive is NULL
        ORDER BY year desc
    ''')

    result = DB.execute(stmt)
    DB.close()

    return result.fetchone()

        
