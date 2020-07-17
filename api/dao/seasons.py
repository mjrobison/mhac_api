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
    season_id                   = UUID
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

def row_mapper(row) -> Season:
    Season = {
        'season_id': row['id'],
        'level': row['level_id'],
        'season_name': row['name'],
        'season_start_date': row['start_date'],
        'roster_submission_deadline': row['roster_submission_deadline'],
        'tournament_start_date': row['tournament_start_date'],
        'sport': row['sport_id'],
        'year': row['year'],
        'slug': row['slug']

    }
    return Season

base_query = '''
SELECT * 
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

def get(slug):
    where = 'WHERE slug = :slug'
    stmt = text('''{base_query} {where} ''')
    result = DB.execute(stmt.bindparams(slug=slug))
    DB.close()
    return row_mapper(result.fetchone())

def archive_season(id):
    pass

def update(season: Season):
    pass

def create(season: Season):
    stmt = text('''INSERT INTO mhac.seasons(id, name, year, level_id, sport_id, start_date, roster_submission_deadline, tournament_start_date, archive) 
                VALUES
                (:id, :name, :year, :level, :sport, :start_date, :roster_submission_deadline, :tournament_start_date, :archive )''')
    DB.execute(stmt.bindparams(id= uuid4(), name= season.season_name, year = season.year, level = season.level, sport = season.sport, start_date =season.start_date , roster_submission_deadline= season.roster_submission_deadline, tournament_start_date = season.tournament_start_date, archive = None))
    DB.commit()
    DB.close()

        
