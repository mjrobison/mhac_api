from fastapi import APIRouter, HTTPException, status, File, UploadFile
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date, time

from dao import tournament

router = APIRouter()


@router.get('/getTournamentInformation', tags=['tournament'])
def get_tournament_games():
    return {'games': tournament.get_tournament_games()}


# @router.post('/addTournamentGame', tags=['games'])
# def add_tournament_game():
#     pass

@router.get('/getActiveTournaments', tags=['tournament'])
def get_active_tournament():
    return tournament.get_tournament()

@router.get('/getTournaments', tags=['tournament'])
def get_tournaments(year):
    return tournament.get_tournament(year=year)

@router.post('/addTournamentGame', tags=['tournament'])
def add_tournament_game(game):
    return tournament.create_tournament_game(game=game)

@router.post("/updateTournamentGame", tags=['tournament'])
def update_tournament_game(game):
    return tournament.update_tournament_game(game=game)