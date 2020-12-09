from fastapi import APIRouter, HTTPException, status, File, UploadFile
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date, time

router = APIRouter()

@router.get('/getTournamentInformation', tags=['tournament'])
def get_tournament_games():
    return {'games': []}

@router.post('/addTournamentGame', tags=['games'])
def add_tournament_game():
    pass