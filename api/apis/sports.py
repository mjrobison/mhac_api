from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date

from dao import sports

router = APIRouter()

class SportBase(BaseModel):
    sport_name: str

class SportOut(SportBase):
    sport_id: int

@router.get('/getSport/<id>', response_model=SportOut, tags=['sport'])
def get_sport(id: int):
    sport = sports.get(id)
    if not sport:
        raise HTTPException(status_code=404, detail="Sport not found")
    return sport

@router.get('/getSports/', response_model=List[SportOut], tags=['sport'])
def get_all_sport():
    sport = sports.get_list()
    if not sport:
        raise HTTPException(status_code=404, detail="Sport not found")
    return sport
    
@router.post('/addSport', tags=['sport'])
def add_sport(sport: SportBase):
    return sports.create(sport)