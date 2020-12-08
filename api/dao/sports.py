from sqlalchemy import Column, String
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric

from sqlalchemy.sql import text # type: ignore
from typing import TypedDict, List, Dict, Any, Optional
from uuid import uuid4, UUID
# from sqlalchemy.dialects.postgresql import JSON, UUID
from datetime import date, timedelta, datetime
from database import db



class Sport(TypedDict):
    id = int
    sport_name = str
    # relationship('Season', backref=('sport_season'))

def row_mapper(row) -> Sport:
    Sport = {
        'sport_id': row['id'],
        'sport_name': row['sport_name']
    }
    return Sport

def get(id):
    DB = db()
    stmt = text('''SELECT * FROM mhac.sports WHERE id = :id ''')
    stmt = stmt.bindparams(id=id)
    result =  DB.execute(stmt)
    row = result.fetchone()
    
    DB.close()
    if not row:
        return None
    return row_mapper(row)

def get_list():
    DB = db()
    sport_list = []
    stmt = text('''SELECT * FROM mhac.sports ''')
    results = DB.execute(stmt)
    DB.close()
    for row in results:
        sport_list.append(row_mapper(row))
    
    return sport_list
    
def create(sport):
    #TODO: Return SPORT_ID or Sport
    DB = db()
    try:
        stmt = text('''INSERT INTO mhac.sports(sport_name) values (:sport_name) RETURNING id''')
        result = DB.execute(stmt.bindparams(sport_name = sport.sport_name))
        DB.commit()
    except Exception as exc:
        return {400: str(exc)}
    DB.close()
    return get(result.fetchone()[0])