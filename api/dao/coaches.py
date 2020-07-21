from sqlalchemy import Column, String
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric

from sqlalchemy.sql import text # type: ignore
from typing import TypedDict, List, Dict, Any, Optional
from uuid import uuid4, UUID
# from sqlalchemy.dialects.postgresql import JSON, UUID
from datetime import date, timedelta, datetime
from database import db

DB = db()

class Person(TypedDict):
    id: str
    first_name= str 
    last_name= str 
    person_type = int
    team_id = str

class Coach(TypedDict):
    first_name= str 
    last_name= str 
    person_type = int
    team_id = str

def create_coach(coach: Coach):
    DB = db()
    print(uuid4())
    stmt = text('''INSERT INTO mhac.person (id, first_name, last_name, person_type, team_id) VALUES (:id, :first_name, :last_name, :person_type, :team_id) ''')
    stmt = stmt.bindparams(id = uuid4(), person_type=2, first_name = coach.first_name, last_name = coach.last_name, team_id= coach.team)
    result = DB.execute(stmt)
    DB.commit()
    DB.close()
    

#TODO: ADD COACHES