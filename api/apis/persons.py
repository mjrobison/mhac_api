from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date

from dao import persons as players
from .teams import TeamBase

router = APIRouter()

class PersonBase(BaseModel):
    first_name: str
    last_name: str
    person_type: str
    team: Optional[UUID]
    
class PlayerOut(PersonBase):
    id: UUID
    team_id: UUID 
    birth_date: Optional[date]
    height: Optional[str]
    person_type: Optional[int]
    player_number: Optional[int]
    position: Optional[int]
    age: Optional[int]


class PlayerIn(PersonBase):
    #TODO: Lookup the season start_date for the Validator
    id: UUID
    first_name: str
    last_name: str
    birth_date: date
    height: Optional[str]
    person_type: str
    number: Optional[int]
    position: Optional[str]

    @validator('birth_date')
    def age_between(cls, birthday):
        min_year = datetime.today().year - 13
        max_year = datetime.today().year - 18
        if not (birthday <= date(min_year, 9, 1) and birthday >= date(max_year, 9,1)):
            raise ValueError("Player must be 18 or younger on September 1st, of the current season.")
        return birthday


#TODO: Move to Rosters
@router.get('/getPlayers/{slug}', response_model=List[PlayerOut], summary='Get a teams players', tags=['players'])
def get_team_players(slug):
    return players.get_team_list(slug)

@router.get('/getPlayers', response_model=List[PlayerOut], summary="Get all players", tags=['players']  )
def get_all_players():
    return players.get_list(person_type='Player')


# @router.get('/getPlayers/{id}', response_model=PlayerOut, tags=['players'])
# def get_a_player(id):
#     return players.get(id)

@router.post('/addPlayer', tags=['players'])
def add_player(player: PlayerIn):
    # try:
        #TODO: Maybe some logic here?
    players.create_player(player)
    # except Exception as exc:
    #     print(str(exc))
    #     raise HTTPException(status_code=404, detail=exc)
    return {200: "Success"}

@router.post('/updatePlayer/{id}', summary="Update a player", tags=['players', 'rosters'])
@router.put('/updatePlayer/{id}', summary="Update a player", tags=['players', 'rosters'])
def update_player(id, player: PlayerIn):
    try:
        print(player)
        players.update(id, player)
    except Exception as exc:
        print(str(exc))
        return {400: "Error Message"}
    return {200: "Success"}

@router.post('/addPlayerToRoster')
def add_to_roster():
    pass

@router.get('/getRoster/{season_team}')
def get_team_roster():
    pass