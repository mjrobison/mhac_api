from sqlalchemy import Column, String
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric

from sqlalchemy.sql import text # type: ignore
from typing import TypedDict, List, Dict, Any, Optional
from uuid import uuid4, UUID
# from sqlalchemy.dialects.postgresql import JSON, UUID
from datetime import date, timedelta, datetime
from database import db

DB = db()

class Game(TypedDict):
    game_id =  UUID
    home_team = dict
    away_team = dict
    final_home_score = int
    final_away_score = int

class GameResult(TypedDict):
    game_id = UUID
    period = int
    home_score = int
    away_score = int
    game_order = int

class Schedule(TypedDict):
    game_id = UUID
    game_date = date
    game_time = datetime
    season = dict
    neutral_site = bool

def get():
    pass

def create():
    pass

def get_list():
    pass

def update():
    pass

def add_period_score():
    pass

def add_final_score():
    pass


