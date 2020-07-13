from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date

from dao import seasons
from .teams import TeamBase

router = APIRouter()

class GameBase(BaseModel):
    game_id: UUID
    home_team: TeamBase
    away_team: TeamBase
    final_home_score: int
    final_away_score: int

@router.get('/getGame', response_model=GameBase, tags=['games'])
def get_game():
    pass

@router.post('/addGame', tags=['games'])
def add_game():
    pass

@router.post('/addPeriodScore', tags=['games'])
def enter_new_period_score():
    pass

@router.put('/updatePeriodScore', tags=['games'])
def update_period():
    pass

@router.post('/updateFinalScore', tags=['games'])
@router.put('/updateFinalScore', tags=['games'])
def update_final_score():
    pass

@router.put('/updateGame', tags=['games'])
def update_game():
    pass