from fastapi import APIRouter, HTTPException, status, File, UploadFile
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date, time

from .seasons import SeasonBase, SeasonOut
from .teams import TeamBase, SeasonTeamOut2 as SeasonTeam
from .persons import PlayerOut 
from dao import games

router = APIRouter()

class GameBase(BaseModel):
    # home_team: TeamBase
    # away_team: TeamBase
    home_team: UUID
    away_team: UUID
    final_home_score: Optional[int]
    final_away_score: Optional[int]

class GameIn(GameBase):
    game_id: UUID

class GameInDel(BaseModel):
    game_id: UUID

class GameResult(BaseModel):
    period: str
    home_score: Optional[int]
    away_score: Optional[int]
    game_order: Optional[int]

class Schedule(GameBase):
    date: date
    time: Optional[time]
    season: UUID
    neutral_site: Optional[str]

class ScheduleUpdate(Schedule):
    game_id: UUID

class Final_Scores(BaseModel):
    away_score: Optional[int]
    home_score: Optional[int]

class Player_Stats(BaseModel):
    player_id: UUID
    game_played: Optional[bool]
    FGA: int
    FGM: int    
    ThreePA: int
    ThreePM: int
    AST: int
    BLK: int
    DREB: int
    FTA: int
    FTM: int
    OREB: int
    STEAL: int
    TO: int
    assists: int
    blocks: int
    defensive_rebounds: int
    offensive_rebounds: int
    steals: int
    total_points: int
    total_rebounds: int
    
class ScheduleOut(Schedule):
    home_team: SeasonTeam
    away_team: SeasonTeam
    final_scores: Final_Scores

class TeamSchedule(BaseModel):
    schedule_id: int
    game_date: date
    game_time: time
    game_id: UUID
    home_team: SeasonTeam
    away_team: SeasonTeam
    final_scores: Final_Scores
    missing_stats: Optional[bool]
    season: SeasonOut

class GameStats(BaseModel):
    game_id: UUID
    team_id: UUID
    game_scores: Optional[List[GameResult]]
    final_scores: Final_Scores
    player_stats: List[Player_Stats]


class GameResultsStatsOut(PlayerOut):
    player_stats: Player_Stats

@router.post('/addGame', tags=['games'])
def add_game(game: Schedule):
    # print(game)
    if game.neutral_site == '':
        game.neutral_site = False
    return games.create(game)

@router.post('/addPeriodScore', tags=['games'])
def enter_new_period_score(game: GameResult):
    return games.add_period_score(game)

@router.put('/updatePeriodScore', tags=['games'])
def update_period(game_result: GameResult):
    return games.update_period_score(game_result)

@router.post('/updateGame', tags=['games'])
def update_game(game: ScheduleUpdate):
    # print(game)
    # return ''
    return games.update(game)

@router.get('/getGameResults/{game_id}') #, response_model=List[GameResultsStatsOut], tags=['games'])
@router.get('/getGameResults/{game_id}/{team_id}') #, response_model=List[GameResultsStatsOut], tags=['games'])
def get_game(game_id: UUID, team_id: UUID= None):
    return games.get_game_results(game_id=game_id, team_id=team_id)

@router.post('/addGameResults/{game_id}', tags=['games'])
def add_game_results(game_id: UUID, game_scores: GameStats):
    return games.add_games_and_stats(game_scores)

@router.post('/addFileGameStats/{game_id}/{team_id}')
async def create_upload_file(game_id: UUID, team_id:UUID, file: UploadFile = File(...) ):
    contents = await file.read()
    msg = games.parse_csv(contents, game_id, team_id)
    missing_players = msg.get('missing_players')
    if missing_players:
        raise HTTPException(status_code=400, detail=missing_players)
    return msg


@router.put('/updateFinalScore', tags=['games'])
def update_final_score():
    pass

@router.post('/addFinalScore', tags=['games'])
def add_final_score(game: GameIn):
    return games.add_final_score(game)

@router.get('/getSchedule/') #, response_model=List[ScheduleOut], tags=['games'])
def get_full_schedules():
    return games.get_team_schedule()

@router.get('/getSchedule/{season_id}', response_model=List[TeamSchedule], tags=['games'])
def get_season_schedules(season_id: UUID):
    return games.get_season_schedule(season_id)

@router.get('/getProgramSchedule/{slug}', response_model=List[TeamSchedule], tags=['games', 'test'])
def get_program_schedules(slug: str):
    return games.get_program_schedule(slug=slug)


@router.get('/getSchedule/{season_id}/{slug}', response_model=List[TeamSchedule], tags=['games', 'test'])
def get_schedules(season_id: UUID, slug: str= None):
    return games.get_team_schedule(season_id=season_id, slug=slug)

@router.get('/getSchedule/{season_team_id}', response_model=List[TeamSchedule], tags=['games'])
def get_team_schedule(season_team_id: UUID):
    return games.get_team_schedule(season_team_id=season_team_id)

@router.post('/deleteGame', tags=['games', 'test'])
def delete_game(game_id: GameInDel):
    try:
        games.remove_game(game_id)
        return {'200': 'success'}
    except:
        return {'400': 'There was a problem'}
