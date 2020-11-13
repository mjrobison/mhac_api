from sqlalchemy import Column, String
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric

from sqlalchemy.sql import text # type: ignore
from typing import TypedDict, List, Dict, Any, Optional
from uuid import uuid4, UUID
# from sqlalchemy.dialects.postgresql import JSON, UUID
from datetime import date, timedelta, datetime
from database import db

from .teams import get_with_uuid as get_team, SeasonTeam
from .levels import get_by_id

DB = db()

class Person(TypedDict):
    first_name= str 
    last_name= str 
    person_type = int
    team = UUID
    team_id = UUID
    birth_date: Date 
    height= Optional[str]
    number = int
    position = Optional[str]


class PlayerCreate(TypedDict):
    first_name= str 
    last_name= str 
    person_type = int
    team = UUID
    season_roster = List[SeasonTeam]
    birth_date: Date 
    height= Optional[str]
    player_number = int
    position = Optional[str]

class PlayerReturn(Person):
    id: UUID
    season_roster: Optional[List[str]]


def player_row_mapper(row) -> PlayerReturn:
    PlayerReturn = {
        'id': row['id'],
        'first_name': row['first_name'],
        'last_name': row['last_name'],
        'birth_date': row['birth_date'],
        'height': row['height'],
        #TODO: Provide a lookup, 
        'person_type': row['person_type'],
        'team': row['team_id'],
        'team_id': row['team_id'],
        'player_number': row['number'],
        'position': row['position'],
        'season_roster': [get_team(i) for i in row['season_roster'].split(',')]
    }
    return PlayerReturn


def get(id) -> Person:
    DB = db()
    stmt = text('''SELECT person.* FROM mhac.person WHERE id = :id ''')
    stmt = stmt.bindparams(id = id)
    result = DB.execute(stmt)
    row = result.fetchone()
    DB.close()
    if row is None:
        raise LookupError(f'Could not find key value with id: {id}')
    else:
        return PlayerCreate

def get_list(person_type) -> List[Person]:
    DB = db()
    player_list = []
    stmt = text('''SELECT person.* FROM mhac.person INNER JOIN mhac.person_type ON person.person_type = person_type.id WHERE person_type.type = :person_type ''')
    result = DB.execute(stmt.bindparams(person_type = person_type))
    DB.close()
    for row in result:
        player_list.append(player_row_mapper(row))
    
    return player_list

def get_team_list(slug):
    DB = db()
    player_list = []
    # stmt = text('''SELECT person.* FROM mhac.person 
    # INNER JOIN mhac.person_type 
    # ON person.person_type = person_type.id
    # INNER JOIN mhac.teams 
    #     ON person.team_id = teams.id 
    # WHERE person_type.type = 'Player' and slug = :slug''')
    stmt = text(''' 
SELECT person.*, string_agg(season_team_id::text, ',') AS season_roster, string_agg(level_id::text,',') 
FROM mhac.team_rosters
INNER JOIN mhac.season_teams_with_names as teams
    ON team_rosters.season_team_id = teams.id 
INNER JOIN mhac.person
    ON team_rosters.player_id = person.id
INNER JOIN mhac.seasons
    ON seasons.id = teams.season_id
WHERE teams.archive is null
and teams.slug = :slug
GROUP BY person.id, person.first_name, person.last_name, person.birth_date, person.height, person.person_type, person.team_id, person.number, person.position''')
    stmt = stmt.bindparams(slug = slug)
    result = DB.execute(stmt)
    DB.close()
    for row in result:
        player_list.append(player_row_mapper(row))
    print(player_list)
    return player_list

def update(id, Player: PlayerCreate):
    #TODO: Compare incoming with existing and update the new field
    print(str(Player))
    stmt = text('''UPDATE mhac.person 
    SET first_name = :first_name, last_name = :last_name, birth_date = :birth_date, position = :position, height = :height, number = :player_number, person_type = :person_type
    WHERE id = :id''')
    stmt = stmt.bindparams(first_name = Player.first_name, last_name=Player.last_name, birth_date = Player.birth_date, position=Player.position, height= Player.height, player_number = Player.player_number, id = Player.id, person_type = '1')
    result = DB.execute(stmt)
    DB.commit()
    DB.close()
    return result
    
def create_player(player: PlayerCreate):
    DB = db()

    message = ''
    try:
        player_id = uuid4()
        stmt = text('''INSERT INTO mhac.person (id, first_name, last_name, birth_date, height, number, position, person_type, team_id) 
        VALUES (:id, :first_name, :last_name, :birth_date, :height, :number, :position, :person_type, :team_id) ''')
        stmt = stmt.bindparams(id = player_id, first_name =player.first_name, last_name = player.last_name, birth_date = player.birth_date, height = player.height, number= player.player_number, position = player.position, person_type = '1', team_id= player.team)
        DB.execute(stmt)

        for season_team in player.season_roster:
            print(season_team)
            stmt = text('''INSERT INTO mhac.team_rosters(season_team_id, player_id)
            VALUES
            (:season_team_id, :player_id) ''')
            stmt = stmt.bindparams(season_team_id = season_team.team_id, player_id = player_id)

            DB.execute(stmt)

        DB.commit()
        message = 'Successfully added player'
        #TODO: Add to a "roster"
    except Exception as exc:
        message =  str(exc)
        print(str(exc))
        DB.rollback()
        raise
    finally:
        DB.close()

    
    # return result

