from sqlalchemy import Column, String
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric

from sqlalchemy.sql import text # type: ignore
from typing import TypedDict, List, Dict, Any
from uuid import uuid4
from sqlalchemy.dialects.postgresql import JSON, UUID

from database import db

DB = db()

class Team(TypedDict):
    team_name: str
    team_mascot: str
    # address_id: address.address_id
    main_color: str
    secondary_color: str
    website: str
    logo_color: str
    logo_grey: str
    slug: str

class TeamOut(Team):
    id: UUID

class SeasonTeam(TypedDict):
    team_id: UUID
    season_id: UUID


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
        'slug': row['slug']
    }
    return Team


def get(slug: str) -> List[TeamOut]:
    team_list = []
    NEW_DB = db()
    stmt = text('''SELECT * FROM mhac.season_teams_with_names WHERE slug = :slug and archive is null''')
    stmt = stmt.bindparams(slug = slug)
    result = NEW_DB.execute(stmt)
    NEW_DB.close()
        # result = DB.execute(stmt)
    for row in result:
        team_list.append(row_mapper(row))
    
    return team_list

    # if row is None:
    #     raise LookupError(f'Could not find key value with id: {id}')
    # else:
    #     key = row_mapper(row)
    #     return key

def get_list() -> List[TeamOut]:
    team_list = []
    stmt = text('''SELECT * FROM mhac.teams''')
    result = DB.execute(stmt)
    for row in result:
        team_list.append(row_mapper(row))
    
    return team_list

def get_with_uuid(id: UUID) -> TeamOut:
    stmt = text('''SELECT * FROM mhac.season_teams_with_names WHERE id = :id''')

    stmt = stmt.bindparams(id = id)
    result = DB.execute(stmt)
    row = result.fetchone()
    result.close()
    if row is None:
        raise LookupError(f'Could not find key value with id: {id}')
    else:
        key = row_mapper(row)
        return key

def create(team: Team):
    #TODO: Validate SeasonId
    stmt = text('''INSERT INTO mhac.teams (id,team_name,team_mascot,address_id,main_color,secondary_color,website,logo_color,logo_grey,slug)
                   VALUES
                    (id,:team_name,:team_mascot,:address_id,:main_color,:secondary_color,:website,:logo_color,:logo_grey,:slug)''')
    stmt = stmt.bindparams(id=uuid4,team_name = team_name, team_mascot=team_mascot,address_id =address_id, main_color=main_color,secondary_color=secondary_color,website=website,logo_color=logo_color,logo_grey=logo_grey,slug=slug)

    DB = db()
    results = DB.execute(stmt)
    DB.commit()
    DB.close()
    return results


def add_to_season(season_team: SeasonTeam):
    stmt = text('''INSERT INTO mhac.season_teams (id, season_id, team_id)
                   VALUES
                    (:id, :season_id, :team_id)''')
    stmt = stmt.bindparams(id=uuid4, season_id=season_team.season_id, team_id=season_team.team_id)

    DB = db()
    results = DB.execute(stmt)
    DB.commit()
    DB.close()
    return results
