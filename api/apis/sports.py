from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date

from dao import sports

router = APIRouter()

class SportBase(BaseModel):

    sport_id: int
    sport_name: str

@router.get('/getSport/<id>', response_model=SportBase, tags=['sport'])
def get_sport(id):
    return sports.get()

@router.post('/addSport', tags=['sport'])
def add_sport():
    pass