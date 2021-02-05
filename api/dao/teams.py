from fastapi import Depends
from sqlalchemy import Column, String
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric

from sqlalchemy.sql import text # type: ignore
from typing import TypedDict, List, Dict, Any
from uuid import uuid4
from sqlalchemy.dialects.postgresql import JSON, UUID

from .addresses import get_address_with_id, Address
from database import db, get_db

DB = db()

class Team(TypedDict):
    team_name: str
    team_mascot: str
    main_color: str
    secondary_color: str
    website: str
    logo_color: str
    logo_grey: str
    slug: str
    

class TeamOut(Team):
    team_id: UUID
    address: Address

class SeasonTeam(Team):
    team_id: UUID
    season_id: UUID
    level_name: str
    select_team_name:str


def row_mapper(row) -> TeamOut:
    Team = {
        'team_id': row['id'],
        'team_name': row['team_name'],
        'team_mascot': row['team_mascot'],
        'main_color': row['main_color'],
        'secondary_color': row['secondary_color'],
        'website': row['website'],
        'logo_color': row['logo_color'],
        'logo_grey': row['logo_grey'],
        'slug': row['slug'],
        'address': get_address_with_id(row['address_id'])
    }
    return Team

def season_team_row_mapper(row) -> SeasonTeam:
    SeasonTeam = {
        'team_id': row['id'],
        # 'team_name': row['team_name'],
        'team_mascot': row['team_mascot'],
        'main_color': row['main_color'],
        'secondary_color': row['secondary_color'],
        'website': row['website'],
        'logo_color': row['logo_color'],
        'logo_grey': row['logo_grey'],
        'slug': row['slug'],
        'season_id': row['season_id'],
        'level_name': row['level_name'],
        'team_name': row['team_name']
    }
    return SeasonTeam


def get(slug: str, DB = db()) -> List[Team]:
    
    team_list = []
    stmt = text('''SELECT * FROM mhac.season_teams_with_names WHERE slug = :slug and archive is null''')
    stmt = stmt.bindparams(slug = slug)
    result = DB.execute(stmt).fetchall()
    for row in result:
        team_list.append(row_mapper(row))
    DB.close()
    return team_list

def _get_slug_by_level_id(id: str):
    team_list = []
    stmt = text('''SELECT * FROM mhac.season_teams_with_names WHERE id = :id and archive is null''')
    stmt = stmt.bindparams(id = id)
    result = DB.execute(stmt)
        # result = DB.execute(stmt)
    DB.close()
    for row in result:
        team_list.append(row_mapper(row))
    
    return team_list[0]

def get_season_teams(slug: str= None) -> List[SeasonTeam]:
    team_name = ''
    if slug:
        team_name = text("""AND slug = :slug """)
    
    DB = db()
    team_list = []
    stmt = text(f'''SELECT * FROM mhac.season_teams_with_names 
        WHERE archive is null
        {team_name}''')
    # print(stmt)
    if slug:
        stmt = stmt.bindparams(slug = slug)

    result = DB.execute(stmt)
        # result = DB.execute(stmt)
    DB.close()
    for row in result:
        team_list.append(season_team_row_mapper(row))
    
    return team_list

def get_season_team(slug: str, seasonid: str) -> SeasonTeam:
    DB = db()
    team_list = []
    stmt = text('''SELECT * FROM mhac.season_teams_with_names WHERE slug = :slug and archive is null and season_id = :seasonid''')
    stmt = stmt.bindparams(slug = slug, seasonid = seasonid)
    result = DB.execute(stmt)
        # result = DB.execute(stmt)
    DB.close()
    return season_team_row_mapper(result.fetchone())


def get_list() -> List[TeamOut]:
    DB = db()
    team_list = []
    stmt = text('''SELECT * FROM mhac.teams''')
    result = DB.execute(stmt)
    DB.close()
    for row in result:
        team_list.append(row_mapper(row))
    
    return team_list

def get_with_uuid(id: UUID) -> SeasonTeam:
    DB = db()
    stmt = text('''SELECT * FROM mhac.season_teams_with_names WHERE id = :id''')

    stmt = stmt.bindparams(id = id)
    result = DB.execute(stmt)
    row = result.fetchone()
    DB.close()
    if row is None:
        raise LookupError(f'Could not find key value with id: {id}')
    else:
        key = season_team_row_mapper(row)
        return key

def create(team: Team):
    DB = db()
    #TODO: Validate SeasonId
    stmt = text('''INSERT INTO mhac.teams (id,team_name,team_mascot,address_id,main_color,secondary_color,website,logo_color,logo_grey,slug)
                   VALUES
                    (id,:team_name,:team_mascot,:address_id,:main_color,:secondary_color,:website,:logo_color,:logo_grey,:slug)''')
    stmt = stmt.bindparams(id=uuid4,team_name = team_name, team_mascot=team_mascot,address_id =address_id, main_color=main_color,secondary_color=secondary_color,website=website,logo_color=logo_color,logo_grey=logo_grey,slug=slug)

    results = DB.execute(stmt)
    DB.commit()
    DB.close()
    return results


def add_to_season(season_team: SeasonTeam):
    DB = db()
    stmt = text('''INSERT INTO mhac.season_teams (id, season_id, team_id)
                   VALUES
                    (:id, :season_id, :team_id)''')
    stmt = stmt.bindparams(id=uuid4, season_id=season_team.season_id, team_id=season_team.team_id)

    results = DB.execute(stmt)
    DB.commit()
    DB.close()
    return results

def get_team_count(DB=db(), season_id=None):
    query = text("""SELECT COUNT(*) FROM mhac.season_teams_with_names WHERE season_id = :season_id""")
    query = query.bindparams(season_id = season_id)
    
    results = DB.execute(query).fetchone()
    results = results[0]
    return results
