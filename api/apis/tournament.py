from fastapi import APIRouter, HTTPException, status, File, UploadFile
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date, time

from dao import tournament

router = APIRouter()

class Game(BaseModel):
    game_number: Optional[int]
    game_date: Optional[date]
    game_time: Optional[time]
    home_team_seed: Optional[int]
    away_team_seed: Optional[int]
    game_description: Optional[str]
    season_id: UUID
    winner_to: Optional[int]
    loser_to: Optional[int]

class GameUpdate(Game):
    home_team_score: Optional[int]
    away_team_score: Optional[int]


@router.get('/getTournamentInformation', tags=['tournament'])
def get_tournament_games():
    return {'games': tournament.get_tournament_games()}

@router.get('/getActiveTournaments', tags=['tournament'])
def get_active_tournament():
    return tournament.get_tournament()

@router.get('/getTournaments', tags=['tournament'])
def get_tournaments(year):
    return tournament.get_tournament(year=year)

@router.post('/addTournamentGame', tags=['tournament'])
def add_tournament_game(game: Game):
    return tournament.create_tournament_game(game=game)

@router.post("/updateTournamentGame", tags=['tournament'])
def update_tournament_game(game: GameUpdate):
    return tournament.update_tournament_game(game=game)