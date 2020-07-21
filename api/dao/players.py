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

class PlayerCreate(Person):
    birth_date: Date 
    height= Optional[str]
    number = int
    position = str

def player_row_mapper(row) -> PlayerCreate:
    PlayerCreate = {
        'id': row['id'],
        'first_name': row['first_name'],
        'last_name': row['last_name'],
        'birth_date': row['birth_date'],
        'height': row['height'],
        #TODO: Provide a lookup, 
        'person_type': row['person_type'],
        'team_id': row['team_id'],
        'number': row['number'],
        'position': row['position']
    }
    return PlayerCreate

def get(id) -> PlayerCreate:
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

def get_list() -> List[PlayerCreate]:
    DB = db()
    player_list = []
    stmt = text('''SELECT person.* FROM mhac.person INNER JOIN mhac.person_type ON person.person_type = person_type.id WHERE person_type.type = 'Player' ''')
    result = DB.execute(stmt)
    DB.close()
    for row in result:
        player_list.append(player_row_mapper(row))
    
    return player_list

def get_team_list(slug):
    player_list = []
    stmt = text('''SELECT * FROM mhac.person INNER JOIN mhac.person_type ON person.person_type = person_type.id WHERE person_type.type = 'Player' and slug = :slug''')
    stmt = stmt.bindparams(team_id = team_id)
    result = DB.execute(stmt)
    for row in result:
        player_list.append(player_row_mapper(row))
    
    return player_list

def update(id, Player: PlayerCreate):
    #TODO: Compare incoming with existing and update the new field
    print(str(Player))
    stmt = text('''UPDATE mhac.person 
    SET first_name = :first_name, last_name = :last_name, birth_date = :birth_date, position = :position, height = :height, number = :player_number, person_type = :person_type
    WHERE id = :id''')
    stmt = stmt.bindparams(first_name = Player.first_name, last_name=Player.last_name, birth_date = Player.birth_date, position=Player.position, height= Player.height, player_number = Player.number, id = Player.id, person_type = '1')
    result = DB.execute(stmt)
    return result
    
def create_player(player: PlayerCreate):
    DB = db()
    print(player)

    stmt = text('''INSERT INTO mhac.person (id, first_name, last_name, birth_date, height, number, position, person_type, team_id) VALUES (:id, :first_name, :last_name, :birth_date, :height, :number, :position, :person_type, :team_id) ''')
    stmt = stmt.bindparams(id = uuid4(), first_name =player.first_name, last_name = player.last_name, birth_date = player.birth_date, height = player.height, number= player.number, position = player.position, person_type =  '1', team_id= player.team_id)
    result = DB.execute(stmt)
    DB.commit()
    DB.close()
    # return result


