from fastapi import Depends
from sqlalchemy import Column, String
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric

from sqlalchemy.sql import text  # type: ignore
from typing import TypedDict, List, Dict, Any, Optional
from uuid import uuid4, UUID

from .addresses import get_address_with_id, Address
from database import db


class Team(TypedDict):
    team_name: str
    team_mascot: str
    main_color: str
    secondary_color: str
    website: Optional[str]
    logo_color: str
    logo_grey: str
    slug: str


class TeamIn(Team):
    active: bool


class TeamOut(Team):
    team_id: UUID
    address: Optional[Address]
    season_id: Optional[UUID]
    active: Boolean


class SeasonTeam(Team):
    team_id: UUID
    season_id: UUID
    level_name: Optional[str]
    select_team_name: Optional[str]


class SeasonTeamUpdate(Team):
    team_id: UUID
    season_id: Optional[UUID]
    address: Optional[Address]
    level_name: Optional[str]


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
        'active': row['active'],
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


def row_mapper_team(row) -> TeamOut:
    Team = {
        'team_id': row['team_id'],
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


def get(slug: str) -> List[Team]:
    team_list = []
    stmt = text('''SELECT * FROM mhac.season_teams_with_names WHERE slug = :slug and archive is null''')
    stmt = stmt.bindparams(slug=slug)
    with db.begin() as DB:
        result = DB.execute(stmt).all()
        for row in result:
            team_list.append(row_mapper(row))
    
    return team_list


def _get_slug_by_level_id(id: str):
    team_list = []
    stmt = text('''SELECT * FROM mhac.season_teams_with_names WHERE id = :id and archive is null''')
    stmt = stmt.bindparams(id=id)
    with db.begin() as DB:
        result = DB.execute(stmt)

        for row in result:
            team_list.append(row_mapper(row))
    return team_list[0]


def get_season_teams(slug: str = None) -> List[SeasonTeam]:
    team_list = []

    print(f"\n\n{slug}\n\n")

    base_query = text(f'''SELECT * FROM mhac.season_teams_with_names 
        WHERE archive is null''')
    team_name = ''
    with db.begin() as DB:
        if slug:
            if type(slug) == UUID:
                team_name = text(f"""{base_query}  AND season_id = :slug """)
                team_name = team_name.bindparams(slug=slug)
                result = DB.execute(team_name)

        
            else:
                team_name = text(f""" {base_query} AND slug = :slug """)
                team_name = team_name.bindparams(slug=slug)
                result = DB.execute(team_name)
                
            for row in result:    
                team_list.append(season_team_row_mapper(row))

        else:
            result = DB.execute(base_query)
            for row in result:    
                team_list.append(season_team_row_mapper(row))

    return team_list


def get_season_team(slug: str, seasonid: str) -> SeasonTeam:
    team_list = []

    print(f"\n\n{slug}, {seasonid}\n\n")

    stmt = text(
        '''SELECT * FROM mhac.season_teams_with_names WHERE slug = :slug and archive is null and season_id = :seasonid''')
    stmt = stmt.bindparams(slug=slug, seasonid=seasonid)
    with db.begin() as DB:
        result = DB.execute(stmt).one()

    return season_team_row_mapper(result)


def get_list() -> List[TeamOut]:
    team_list = []
    with db.begin() as DB:
        stmt = text('''SELECT * FROM mhac.teams WHERE active''')
        result = DB.execute(stmt)

    for row in result:
        team_list.append(row_mapper(row))
    
    return team_list


def get_with_uuid(id: UUID) -> SeasonTeam:
    
    stmt = text('''SELECT * FROM mhac.season_teams_with_names WHERE id = :id''')

    stmt = stmt.bindparams(id=id)
    with db.begin() as DB:
        result = DB.execute(stmt)
        row = result.fetchone()
    
    if row is None:
        # raise LookupError(f'Could not find key value with id: {id}')
        return ''
    else:
        key = season_team_row_mapper(row)
        return key


def admin_get_with_uuid(id: UUID) -> SeasonTeam:
    stmt = text('''SELECT * FROM mhac.season_teams_with_names WHERE id = :id''')

    stmt = stmt.bindparams(id=id)
    with db.begin() as DB:
        result = DB.execute(stmt)
        row = result.fetchone()
    if row is None:
        raise LookupError(f'Could not find key value with id: {id}')
    else:
        key = row_mapper_team(row)
        return key


def create(team: TeamIn):
    
    insert_stmt = text('''INSERT INTO mhac.teams (id,team_name,team_mascot,address_id,main_color,secondary_color,website,logo_color,logo_grey,slug, active)
                   VALUES
                    (uuid_generate_v4(),:team_name,:team_mascot,:address_id,:main_color,:secondary_color,:website,:logo_color,:logo_grey,:slug, :active)''')
    query = text('''SELECT * FROM mhac.addresses limit 1''')

    with db.begin() as DB:
        address_result = DB.execute(query).all()
        
        insert_stmt = insert_stmt.bindparams(team_name=team.team_name, team_mascot=team.team_mascot, address_id=address_result[0][0],
                           main_color=team.main_color, secondary_color=team.secondary_color, website=team.website,
                           logo_color=team.logo_color, logo_grey=team.logo_grey, slug=team.slug, active=team.active)

        print(insert_stmt)
        DB.execute(insert_stmt)
        DB.commit()
        
    return team


def add_to_season(season_team: SeasonTeam):
    stmt = text('''INSERT INTO mhac.season_teams (id, season_id, team_id)
                   VALUES
                    (:id, :season_id, :team_id)''')
    stmt = stmt.bindparams(id=uuid4, season_id=season_team.season_id, team_id=season_team.team_id)
    
    with db.begin() as DB:
        DB.execute(stmt)
        stmt = text('''INSERT INTO mhac.standings (team_id, season_id, wins, losses, games_played, win_percentage, standings_rank)
        VALUES
        (:team_id, :season_id, 0, 0, 0, 0.00, 0) 
        ''')
        stmt = stmt.bindparams(team_id=season_team.team_id, season_id=season_team.season_id)
        DB.execute(stmt)
        DB.commit()

    return season_team


def get_team_count(season_id=None):
    query = text(
        """SELECT COUNT(*) FROM mhac.season_teams_with_names INNER JOIN mhac.standings ON season_teams_with_names.id = standings.team_id WHERE season_teams_with_names.season_id = :season_id AND standings_rank <> 99""")
    query = query.bindparams(season_id=season_id)

    with db.begin() as DB:
        results = DB.execute(query).one()
        
    return results
