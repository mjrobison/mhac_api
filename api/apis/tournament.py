from fastapi import APIRouter, HTTPException, status, File, UploadFile
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date, time

from dao import tournament
from .teams import TeamOut
from .seasons import SeasonOut as Season

router = APIRouter()


class Game(BaseModel):
    game: Optional[int]
    date: Optional[date]
    time: Optional[time]
    game_description: Optional[str]
    home_team_seed: Optional[int]
    away_team_seed: Optional[int]
    display: bool
    seasons: Season
    winner_to: Optional[int]
    loser_to: Optional[int]
    winners_from: Optional[List[int]]


class GameUpdate(Game):
    home_team_score: Optional[int]
    away_team_score: Optional[int]


class MatchUp(BaseModel):
    team1: Optional[str]
    scoreTeam1: Optional[int]
    team1Seed: Optional[int]
    team2: Optional[str]
    scoreTeam2: Optional[int]
    team2Seed: Optional[int]
    winner_to: Optional[str]
    loser_to: Optional[str]


class Location(BaseModel):
    address: str
    name: str


class TournamentGame(BaseModel):
    game: int
    date: date
    time: time
    game_description: str
    matchup: MatchUp
    location: Optional[Location]
    seasons: Season
    display: Optional[bool]
    winners_from: Optional[List[int]]


@router.get('/getTournamentInformation/', tags=['tournament'])
def get_tournament_games(season_id: UUID = None):
    return {'games': tournament.get_tournament_games(season_id=season_id)}


@router.get('/getActiveTournaments/', tags=['tournament'])
def get_active_tournament():
    return tournament.get_tournament()


@router.get('/getTournaments/', tags=['tournament'])
def get_tournaments(year):
    return tournament.get_tournament(year=year)


@router.post('/addTournamentGame/', tags=['tournament'])
def add_tournament_game(tournament_game: TournamentGame):
    return tournament.create_tournament_game(game=tournament_game)


@router.post("/updateTournamentGame/", tags=['tournament'])
def update_tournament_game(tournament_game: TournamentGame):
    print(tournament_game)
    return tournament.update_tournament_game(game=tournament_game)
