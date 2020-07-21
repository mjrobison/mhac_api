from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date

from dao import persons, coaches
from .teams import TeamBase
from .persons import PersonBase

router = APIRouter()

class CoachOut(PersonBase):
    id: UUID


@router.post('/addCoach', tags=['coaches', 'rosters'])
def add_coach(coach: PersonBase):
    try:
        persons.create_coach(coach)
    except Exception as exc:
        print(str(exc))
        return {400: "Error Message"}
    return {200:"Success"}

@router.put('/updateCoach/<id>', tags=['coaches', 'rosters'])
def update_coach(id, coach: PersonBase):
    try:
        persons.update(id, coach)
    except Exception as exc:
        print(str(exc))
        return {400: "Error Message"}
    return {200:"Success"}

@router.get('/getCoaches/', response_model=List[CoachOut], tags=['coaches', 'rosters'], summary="Gets all coaches in the system")
def get_coach_list(team_slug):
    return coaches.get_all_coaches(person_type='Coach')

@router.get('/getCoach/<id>', response_model=CoachOut)
def get_coach():
    return coaches.get_coach(id =id)

def get_team_coaches(team):
    pass

