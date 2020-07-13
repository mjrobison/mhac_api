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
        'sport_name': row['name']
    }

def get():
    pass

def create():
    pass
