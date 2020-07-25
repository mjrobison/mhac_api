from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date

from .seasons import SeasonBase
from .teams import TeamBase
from dao import games

router = APIRouter()

class GameBase(BaseModel):
    # home_team: TeamBase
    # away_team: TeamBase
    home_team: UUID
    away_team: UUID
    final_home_score: Optional[int]
    final_away_score: Optional[int]

class GameIn(GameBase):
    game_id: UUID

class GameResult(GameIn):
    period: int
    home_score: int
    away_score: int
    game_order: Optional[int]

class Schedule(GameBase):
    game_date: date
    game_time: datetime
    season: UUID
    neutral_site: bool

@router.post('/addGame', tags=['games'])
def add_game(game: Schedule):
    return games.create(game)

@router.post('/addTournamentGame', tags=['games'])
def add_game(game: Schedule):
    pass

@router.post('/addPeriodScore', tags=['games'])
def enter_new_period_score(game: GameResult):
    return games.add_period_score(game)

@router.put('/updatePeriodScore', tags=['games'])
def update_period(game_result: GameResult):
    return games.update_period_score(game_result)

@router.put('/updateGame', tags=['games'])
def update_game():
    return games.update()

@router.get('/getGameResults/<game_id>/<team_id>', response_model=GameBase, tags=['games'])
def get_game(game_id):
    pass

@router.post('/addGameResults/<game_id>', tags=['games'])
def add_game_results():
    pass

@router.put('/updateFinalScore', tags=['games'])
def update_final_score():
    pass

@router.post('/addFinalScore', tags=['games'])
def update_final_score(game: GameIn):
    return games.add_final_score(game)

@router.get('/getSchedule')
@router.get('/getSchedule/<season_id>')
@router.get('/getSchedule/<season_id>/<slug>')
def get_schedules():
    pass