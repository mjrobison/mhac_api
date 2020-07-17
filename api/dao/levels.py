from sqlalchemy import Column, String
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric

from sqlalchemy.sql import text # type: ignore
from typing import TypedDict, List, Dict, Any, Optional
from uuid import uuid4, UUID
# from sqlalchemy.dialects.postgresql import JSON, UUID
from datetime import date, timedelta, datetime
from database import db

DB = db()

class Level(TypedDict):
    id = int
    level_name = str

def row_mapper(row) -> Level:
    Level = {
        'id' = row['id']
        'name' = row['name']
    }
    return Level

def get():
    pass

def get_list():
    pass

def create():
    pass

def update():
    pass
