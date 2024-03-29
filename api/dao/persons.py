from fastapi import HTTPException
from sqlalchemy.sql import text # type: ignore
from typing import TypedDict, List, Dict, Any, Optional
from uuid import uuid4, UUID
from database import db

from .teams import get_with_uuid as get_team, SeasonTeam
from .levels import get_level_by_id
from database import db


# DB = db()

class Height(TypedDict):
    feet: Optional[int]
    inches: Optional[int]

class Person(TypedDict):
    first_name: str 
    last_name: str 
    person_type: int
    team: UUID
    team_id: UUID
    age: Optional[int] 
    height: Optional[Height]
    number: int
    position: Optional[str]


class PlayerCreate(TypedDict):
    first_name: str 
    last_name: str 
    person_type: int
    team: UUID
    season_roster: List[SeasonTeam]
    age: Optional[int] 
    height: Optional[Height]
    player_number: Optional[int]
    position: Optional[str]

class PlayerReturn(Person):
    id: UUID
    season_roster: Optional[List[str]]
    age: int

def calc_age(birth_date): 
    from dateutil.relativedelta import relativedelta
    from datetime import date
    return relativedelta(date.today(), birth_date).years

def break_height(inches):
    if inches:
        feet = int(int(inches)/12)
        inches = int(int(inches) % 12)
        return feet, inches
    return 0, 0 

def combine_height(height: Height):
    return (height.feet * 12) + height.inches


def player_row_mapper(row) -> PlayerReturn:
    feet, inches = break_height(row['height'] if row['height'] is not None else 0)
    PlayerReturn = {
        'id': row['id'],
        'first_name': row['first_name'],
        'last_name': row['last_name'],
        'age': row['age'],
        'height': {
            'feet': feet,
            'inches': inches
        },
        #TODO: Provide a lookup, 
        'person_type': row['person_type'],
        'team': row['team_id'],
        'team_id': row['team_id'],
        'player_number': row['number'],
        'position': row['position'],
        'season_roster': [get_team(i) for i in row['season_roster'].split(',')]
    }
    return PlayerReturn

def person_row_mapper(row):
    PersonReturn = {
        'id': row['id'],
        'first_name': row['first_name'],
        'last_name': row['last_name'],
        'age': row['age'],
    }
    return PersonReturn


def get(id) -> Person:
    stmt = text('''SELECT person.* FROM mhac.person WHERE id = :id ''')
    stmt = stmt.bindparams(id = id)
    with db.begin() as DB:
        result = DB.execute(stmt)
        row = result.fetchone()
    
    if row is None:
        raise LookupError(f'Could not find key value with id: {id}')
    else:
        return PlayerCreate

def get_list(person_type=None):
    player_list = []
    stmt = text('''SELECT person.id, 
                        person.first_name
                        , person.last_name
                        , COALESCE(person.age::text, '') AS age
                        , COALESCE(person.height, '') AS height
                        , person_type.type
                        , COALESCE(person.number::text, '') AS number
                        , COALESCE(person.position,'') AS position
                    FROM mhac.person 
                    INNER JOIN mhac.person_type 
                        ON person.person_type = person_type.id 
                    WHERE person_type.type = :person_type ''')
    stmt = stmt.bindparams(person_type=person_type)
    with db.begin() as DB:
        result = DB.execute(stmt)
    
    for row in result:
        player_list.append(person_row_mapper(row))

    return player_list

def get_team_list(slug, season_level: Optional[str] = None, DB=db()):
    player_list = []

    base_query = text(''' 
        SELECT person.id, person.first_name
        , person.last_name
        , person.age
        , person.height
        , person.person_type
        , person.team_id
        , person.position
        , team_rosters.jersey_number as number
        , string_agg(season_team_id::text, ',') AS season_roster
        , string_agg(level_id::text,',') 
        FROM mhac.team_rosters
        INNER JOIN mhac.season_teams_with_names as teams
            ON team_rosters.season_team_id = teams.id 
        INNER JOIN mhac.person
            ON team_rosters.player_id = person.id
        INNER JOIN mhac.seasons
            ON seasons.id = teams.season_id
        WHERE teams.archive is null
        and teams.slug = :slug''')
    group_by = text('''GROUP BY person.id, person.first_name, person.last_name, person.age, person.height, person.person_type, person.team_id, person.position, team_rosters.jersey_number''')

    stmt = text(f"{base_query} {group_by}")
    stmt = stmt.bindparams(slug = slug)
    
    if season_level:
        stmt = text(f"{base_query} and team_rosters.season_team_id = :season_level {group_by}")
        stmt = stmt.bindparams(slug = slug, season_level = season_level)
    
    try:
        with db.begin() as DB:
            result = DB.execute(stmt)
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="No rosters for the team.")
            for row in result:
                player_list.append(player_row_mapper(row))
    except Exception as exc:
        print(str(exc))
        raise
    
    return player_list


def update(id, Player: PlayerCreate, DB=db()):
    #TODO: Compare incoming with existing and update the new field
    #TODO: Remove a seasonTeam
    
    #Check Season Teams
    query = text(""" 
    SELECT * FROM mhac.team_rosters
    INNER JOIN mhac.season_teams_with_names
        ON team_rosters.season_team_id = season_teams_with_names.id
    WHERE player_id = :player_id
        AND season_teams_with_names.archive is null
    """)

    query = query.bindparams(player_id = Player.id)
    with db.begin() as DB:
        results = DB.execute(query).fetchall()

    if len(results) > len(Player.season_roster):
        
        for r in results:
            if r not in Player.season_roster: 
                update = text("""DELETE FROM mhac.team_rosters WHERE roster_id = :roster_id """)
                update = update.bindparams(roster_id = r.roster_id)
                DB.execute(update)

    for season_team in Player.season_roster:
        stmt = text('''INSERT INTO mhac.team_rosters(season_team_id, player_id, jersey_number)
        VALUES
        (:season_team_id, :player_id, :number) 
        ON CONFLICT ON CONSTRAINT ux_season_team_player_id 
        DO UPDATE
        SET jersey_number = :number''')
        
        stmt = stmt.bindparams(season_team_id = season_team.team_id, player_id = id, number = Player.player_number)
        with db.begin() as DB:
            DB.execute(stmt)
            DB.commit()

    player_height = combine_height(Player.height)
    stmt = text('''UPDATE mhac.person 
    SET first_name = :first_name, last_name = :last_name, age = :age, position = :position, height = :height, number = :player_number, person_type = :person_type
    WHERE id = :id''')
    stmt = stmt.bindparams(first_name=Player.first_name,
                           last_name=Player.last_name,
                           age=Player.age,
                           position=Player.position,
                           height=player_height,
                           player_number=Player.player_number,
                           id=Player.id, person_type = '1')

    try:
        with db.begin() as DB:
            DB.execute(stmt)
            DB.commit()
    except Exception as exc:
        print(str(exc))
    finally:
        DB.close()
    
    
def create_player(player):
    message = ''
    
    # player_check_query = text('''SELECT * FROM mhac.person WHERE first_name = :first_name AND last_name = :last_name AND birth_date = :birth_date ''')
    # player_check_query = player_check_query.bindparams(first_name = player.first_name, last_name = player.last_name, birth_date = player.birth_date)
    # results = DB.execute(player_check_query)
    # if results.rowcount < 1:
    # height =  #('height', None)
    # if height:
    
    player_height = combine_height(player.height)
    if player_height == 0:
        player_height = None
    
    player_id = uuid4()
    stmt = text('''INSERT INTO mhac.person (id, first_name, last_name, age, height, number, position, person_type, team_id)
    VALUES (:id, :first_name, :last_name, :age, :height, :number, :position, :person_type, :team_id)
    ON CONFLICT ON CONSTRAINT ux_persons
    DO
    UPDATE
    SET first_name = :first_name, last_name = :last_name, age = :age, height=:height, number = :number, position=:position
    RETURNING id''')
    stmt = stmt.bindparams(id = player_id,
                            first_name =player.first_name,
                            last_name = player.last_name,
                            age = player.age,
                            height = player_height,
                            number= player.player_number,
                            position = player.position,
                            person_type = '1',
                            team_id= player.team_id)
    with db.begin() as DB:
        try:
            result = DB.execute(stmt).fetchone()
            if result:
                player_id = result[0]

            for season_team in player.season_roster:
                stmt = text('''INSERT INTO mhac.team_rosters(season_team_id, player_id, jersey_number)
                VALUES
                (:season_team_id, :player_id, :number)
                ON CONFLICT ON CONSTRAINT ux_season_team_player_id
                DO UPDATE
                SET jersey_number = :number''')
                stmt = stmt.bindparams(season_team_id = season_team.team_id, player_id = player_id, number = player.player_number)

                DB.execute(stmt)

                DB.commit()
        except Exception as exc:
            message =  str(exc)
            print(str(exc))
            DB.rollback()
            raise
    
    return message

    
    
