# from sqlalchemy import Column, String
# from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric

from sqlalchemy.sql import text # type: ignore
from typing import TypedDict, List, Dict, Any, Optional
from uuid import uuid4, UUID
# from sqlalchemy.dialects.postgresql import JSON, UUID
from datetime import date, timedelta, datetime
from database import db

DB = db()

base_query = text('''SELECT * FROM mhac.levels''')

class LevelBase(TypedDict):
    level_name = str

class Level(LevelBase):
    id = int

def row_mapper(row) -> Level:
    Level = {
        'id': row['id'],
        'name': row['level_name']
    }
    return Level

def get_by_id(id) -> Level:
    stmt = text(f'''{base_query } WHERE id = :id''')
    stmt = stmt.bindparams(id = id)
    results = DB.execute(stmt)
    return results.fetchone()

def get_by_name(level_name) -> Level:
    stmt = text(f'''{base_query } WHERE level_name = :level_name''')
    stmt = stmt.bindparams(level_name = level_name)
    results = DB.execute(stmt)
    return results.fetchone()

def get_list() -> List[Level]:
    NEW_DB = db()
    stmt = text(f'''{base_query}''')
    print(stmt)
    # stmt = stmt.bindparams()
    results = NEW_DB.execute(stmt)
    NEW_DB.close()
    level_list = []
    for result in results.fetchall():
        level_list.append(row_mapper(result))
    return level_list
    
def create(level: LevelBase):
    stmt = text('''INSERT INTO mhac.levels(level_name) 
                    VALUES
                    (:level_name)''')
    stmt = stmt.bindparams(level_name = level.level_name)
    
    DB.execute(stmt)
    DB.commit()
    return {200: "Success"}


def update(level: Level):
    stmt = text('''UPDATE mhac.levels
                    SET level_name =:level_name
                    WHERE id = :id ''')
    stmt = stmt.bindparams(id = level.id, level_name = level.level_name)
    
    DB.execute(stmt)
    DB.commit()
    return {200: "Success"}
