from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date
import logging
from dao import persons as players, teams
from .teams import TeamBase, SeasonTeamOut2

router = APIRouter()

class PersonBase(BaseModel):
    first_name: str
    last_name: str
    person_type: Optional[int]
    team_id: Optional[UUID]

class Height(BaseModel):
    feet: Optional[int]
    inches: Optional[int]
    
class PublicPlayerOut(PersonBase):
    id: UUID
    height: Optional[Height]
    player_number: Optional[int]
    position: Optional[str]
    age: Optional[int]
    season_roster: Optional[List[SeasonTeamOut2]]

class PlayerOut(PersonBase):
    id: UUID
    age: Optional[int]
    height: Optional[Height]
    player_number: Optional[int]
    position: Optional[str]
    age: Optional[int]
    season_roster: Optional[List[SeasonTeamOut2]]

class PlayerIn(PersonBase):
    #TODO: Lookup the season start_date for the Validator
    id: Optional[UUID]
    season_roster: List[SeasonTeamOut2]
    age: int
    height: Optional[Height]
    person_type: str
    player_number: Optional[int]
    position: Optional[str]
    

    # @validator('birth_date')
    # def age_between(cls, birthday):
    #     # print(birthday)
    #     min_year = datetime.today().year - 13
    #     max_year = datetime.today().year - 19
    #     if datetime.today().month < 9:
    #         max_year = datetime.today().year - 20

    #     if not (birthday >= date(max_year, 9,1)):
    #         raise ValueError("Player must be 18 or younger on September 1st, of the current season.")
    #     return birthday
    
    # TODO: Convert Feet and inches to inches


#TODO: Move to Rosters
@router.get('/getPlayers/{slug}', response_model=List[PublicPlayerOut], summary='Get a teams players', tags=['players'])
def get_team_players(slug):
    return players.get_team_list(slug)

@router.get('/getPlayers', response_model=List[PublicPlayerOut], summary="Get all players", tags=['players']  )
def get_all_players():
    return players.get_list(person_type='Player')


@router.post('/addPlayer', tags=['players'])
def add_player(player: PlayerIn):
    players.create_player(player)
    return {200: "Success"}

@router.post('/updatePlayer/{id}', summary="Update a player", tags=['players', 'rosters'])
@router.put('/updatePlayer/{id}', summary="Update a player", tags=['players', 'rosters'])
def update_player(id, player: PlayerIn):
    try:
        players.update(id, player)
    except Exception as exc:
        print(str(exc))
        return HTTPException(status_code = 400, detail= "Error Message")
    return {200: "Success"}

@router.post('/addPlayerToRoster')
def add_to_roster():
    pass

@router.get('/getRoster/{season_team}', summary="Get a leveled team roster", tags=['players', 'rosters'])
def get_team_roster(season_team: UUID):
    team = teams._get_slug_by_level_id(season_team).get('slug')
    return players.get_team_list(team, season_team)

#TODO: Move to Rosters
@router.get('/getAdminPlayers/{slug}', response_model=List[PlayerOut], summary='Get a teams players', tags=['players'])
def get_team_players(slug):
    return players.get_team_list(slug)

@router.get('/getAdminPlayers', response_model=List[PlayerOut], summary="Get all players", tags=['players']  )
def get_all_players():
    return players.get_list(person_type='Player')
