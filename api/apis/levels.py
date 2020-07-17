from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date

# from dao import seasons
# from .teams import TeamBase
router = APIRouter()

class LevelBase(BaseModel):
    level_name = str

class LevelOut(LevelBase):
    level_id = int


@router.get('/getLevels')
def get_all_levels():
    pass

@router.get('getLevelByName')
def get_a_level(name):
    pass

@router.post('/addLevel')
def add_level():
    pass

@router.put('/updateLevel')
def update_level():
    pass