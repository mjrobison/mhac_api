from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date

# from dao import persons as players
# from .teams import TeamBase

router = APIRouter()

@router.get('/getStats')
def get_Stats():
    pass