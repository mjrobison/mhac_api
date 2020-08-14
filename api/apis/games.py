from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date

from .seasons import SeasonBase
from .teams import TeamBase
from .persons import PlayerOut 
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

class Final_Scores(BaseModel):
    away_score: int
    home_score: int

class Player_Stats(BaseModel):
    FGA: int
    FGM: int    
    ThreePA: int
    ThreePM: int
    AST: int
    BLK: int
    DREB: int
    FTA: int
    FTM: int
    OREB: int
    STEAL: int
    TO: int
    assists: int
    blocks: int
    defensive_rebounds: int
    offensive_rebounds: int
    steals: int
    total_points: int
    total_rebounds: int

class ScheduleOut(GameBase):
    pass

# class players(PersonBase):
#     player_stats: List[Player_Stats]

class GameResultsStatsOut(PlayerOut):
    # pass
    player_stats: Player_Stats


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

@router.get('/getGameResults/<game_id>/<team_id>', response_model=List[GameResultsStatsOut], tags=['games'])
def get_game(game_id: UUID, team_id: UUID):
    # print(games.get_game_results(game_id=game_id, team_id=team_id))
    return games.get_game_results(game_id=game_id, team_id=team_id)

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
@router.get('/getSchedule/<season_id>/<slug>', response_model=List[ScheduleOut], tags=['games'])
def get_schedules():
    pass