from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator

from dao import levels

router = APIRouter()


class LevelBase(BaseModel):
    level_name: str


class LevelOut(LevelBase):
    id: int


@router.get('/getLevels', response_model=List[LevelOut], tags=['level'])
def get_all_levels() -> List[LevelOut]:
    return levels.get_list()


@router.get('/getLevelByName/{name}',  tags=['level'])
def get_a_level(name) -> LevelOut:
    return levels.get_by_name(name)


@router.get('/getLevelByID/{id}', tags=['level'])
def get_a_level_by_id(id):
    return levels.get_level_by_id(id)


@router.post('/addLevel', tags=['level'])
def add_level(level: LevelBase):
    return levels.create(level)


@router.put('/updateLevel', tags=['level'])
def update_level(level: LevelOut):
    return levels.update(level)