from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date

from dao import players

router = APIRouter()

class PlayerBase(BaseModel):
    first_name: str
    last_name: str
    birth_date: Optional[date]
    height: Optional[str]
    person_type: str
    team_id: UUID
    number: Optional[int]
    position: Optional[str]

class PlayerOut(PlayerBase):
    id: UUID

class PlayerIn(PlayerBase):
    #TODO: Lookup the season start_date for the Validator
    id: UUID
    first_name: str
    last_name: str
    birth_date: date
    height: Optional[str]
    person_type: str
    team_id: UUID
    number: Optional[int]
    position: Optional[str]

    @validator('birth_date')
    def age_between(cls, birthday):
        min_year = datetime.today().year - 13
        max_year = datetime.today().year - 18
        if not (birthday <= date(min_year, 9, 1) and birthday >= date(max_year, 9,1)):
            raise ValueError("Player must be 18 or younger on September 1st, of the current season.")
        return birthday



@router.get('/getPlayers', response_model=List[PlayerOut], summary="Get all players")
def get_all_players():
    return players.get_list()

#TODO: Move to Rosters
@router.get('/getPlayers/<slug>', response_model=List[PlayerOut], summary='Get a teams players')
def get_team_players(slug):
    return players.get_team_list()

@router.get('/getPlayers/<id>', response_model=PlayerOut)
def get_a_player(id):
    return players.get(id)

@router.post('/addPlayer')
def add_player(player: PlayerIn):
    # try:
        #TODO: Maybe some logic here?
    players.create(player)
    # except Exception as exc:
    #     print(str(exc))
    #     raise HTTPException(status_code=404, detail=exc)
    return {200: "Success"}

@router.post('/updatePlayer/<id>', summary="Update a player")
@router.put('/updatePlayer/<id>', summary="Update a player")
def update_player(id, player: PlayerIn):
    try:
        print(player)
        players.update(id, player)
    except Exception as exc:
        print(str(exc))
        return {400: "Error Message"}
    return {200: "Success"}