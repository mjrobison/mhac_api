from fastapi import APIRouter, HTTPException, UploadFile
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date
import logging
import io
import openpyxl
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
    id: Optional[UUID]
    season_roster: List[SeasonTeamOut2]
    age: int
    height: Optional[Height]
    person_type: str
    player_number: Optional[int]
    position: Optional[str]

class ImportPlayer(BaseModel):
    first_name: str
    last_name: str
    team_slug: str
    year: str
    level_name: str
    age: int
    height: Optional[Height]
    player_number: Optional[int]
    position: Optional[str]
    grade: int


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

@router.post('/addPlayerToRoster', tags=['players'])
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


@router.post('/teamFile')
async def create_team_file(file: UploadFile, team_slug: str, level_name: str, year: str):
    #TODO: Needs season_roster: List[SeasonTeamOut2]
    # print(file.filename, team_id)
    if file.filename.endswith('.xlsx'):
        f = await file.read()
        xlsx = io.BytesIO(f)
        wb = openpyxl.load_workbook(xlsx)
        ws = wb.active
        
        import re
        pattern = re.compile(r"""(\d+)(?:'|’)(?: *(\d+))?""")
        headers = ['player_number', 'age', 'grade', 'position', 'height', 'first_name', 'last_name']
        response_list = []
        # From the excel file players start in A4
        for row in ws.iter_rows(min_row=4):
            row_values = [cell.value for cell in row]
            if set(row_values) != set([None]):
                person = dict(zip(headers, [cell.value for cell in row]))
                feet, inches = re.match(pattern, person['height']).groups()
            
                person['height'] = {
                    'feet': int(feet or 0),
                    'inches': int(inches or 0)
                }
                
                person['level_name'] = level_name
                person['team_slug'] = team_slug
                person['year'] = year
                person['person_type'] = '1'
                
                response_list.append(players.import_player(ImportPlayer(**person)))

        return response_list

        