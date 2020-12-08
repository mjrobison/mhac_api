from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date

from dao import levels

router = APIRouter()

class LevelBase(BaseModel):
    level_name = str

class LevelOut(LevelBase):
    level_id = int


@router.get('/getLevels')
def get_all_levels():
    return levels.get_list()

@router.get('/getLevelByName/{name}')
def get_a_level(name):
    return levels.get_by_name(name)

@router.get('/getLevelByID/{id}')
def get_a_level_by_id(id):
    return levels.get_by_id(id)

@router.post('/addLevel')
def add_level(level: LevelBase):
    return levels.create(level)

@router.put('/updateLevel')
def update_level(level: LevelOut):
    return levels.update(level)