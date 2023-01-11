from sqlalchemy import Column, String
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric

from sqlalchemy.sql import text # type: ignore
from typing import TypedDict, List, Dict, Any, Optional
from uuid import uuid4, UUID
# from sqlalchemy.dialects.postgresql import JSON, UUID
from datetime import date, timedelta, datetime
from database import db

from .persons import Person

DB = db()

class Coach(Person):
    first_name: str
    last_name: str
    person_type: int
    team_id: str

class CoachOut(Coach):
    id: UUID
    first_name: str
    last_name: str
    person_type: int
    team_id: str


def coach_row_mapper(row) -> CoachOut:
    Coach = {
        'id': row['id'],
        'first_name': row['first_name'],
        'last_name': row['last_name'],
        'person_type': row['type'],
        #TODO: map to getting a team (OR seasonTeam)
        'team': row['team_id'] #get_team(row['team_id'])
    }
    return CoachOut

def create_coach(coach: Coach):
    with db.begin() as DB:
        stmt = text('''INSERT INTO mhac.person (id, first_name, last_name, person_type, team_id) VALUES (:id, :first_name, :last_name, :person_type, :team_id) ''')
        stmt = stmt.bindparams(id = uuid4(), person_type=2, first_name = coach.first_name, last_name = coach.last_name, team_id= coach.team)
        result = DB.execute(stmt)
        DB.commit()


def get_coach(id) -> CoachOut:
    with db.begin() as DB:
        stmt = text('''SELECT person.* FROM mhac.person WHERE id = :id ''')
        stmt = stmt.bindparams(id = id)
        result = DB.execute(stmt)
        row = result.fetchone()
    
    if row is None:
        raise LookupError(f'Could not find key value with id: {id}')
    else:
        return PlayerCreate

def get_coach_list(person_type) -> List[CoachOut]:
    #TODO: Get Coaches of an individual season team
    DB = db()
    player_list = []
    print(person_type)
    stmt = text('''SELECT person.id, person.first_name, person.last_name, person_type.type, person.team_id FROM mhac.person INNER JOIN mhac.person_type ON person.person_type = person_type.id WHERE person_type.type = :person_type ''')
    result = DB.execute(stmt.bindparams(person_type = person_type))
    DB.close()
    for row in result:
        player_list.append(coach_row_mapper(row))

    return player_list

def get_all_coaches() -> List[CoachOut]:
    person_type='2'

    player_list = []
    with db.begin() as DB:
        stmt = text('''SELECT person.id, person.first_name, person.last_name, person_type.type, person.team_id 
        FROM mhac.person 
        INNER JOIN mhac.person_type 
            ON person.person_type = person_type.id 
        WHERE person_type.type = :person_type ''')
        result = DB.execute(stmt.bindparams(person_type = person_type))
    
    for row in result:
        player_list.append(coach_row_mapper(row))
    
    return player_list
