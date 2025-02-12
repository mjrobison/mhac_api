from fastapi import APIRouter, HTTPException, status, File, UploadFile
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date, time

from dao import tournament
from .teams import TeamOut
from .seasons import SeasonOut as Season
from dao.standings import get_a_season

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



from typing import List, Dict, Union



# Global state for storing the tournament data
tournament_state = {"bracket": {}, "scores": {}}


@router.post("/tournament/init/{season_id}", tags=['tournament_new'])
def initialize_tournament(season_id):
    """
    Initialize the tournament brackets.
    """
    print(season_id)
    teams = get_a_season(season_id)
    
    tournament_state["bracket"] = tournament.generate_bracket(teams)
    tournament_state["scores"] = {}
    return tournament_state["bracket"]

class update_score(BaseModel): 
    match_id: int
    winner_id: int
    loser_id: int

@router.post("/tournament/update_score", tags=['tournament_new'])
def update_score(data: update_score) -> Dict:
    """
    Update match score and dynamically update the bracket.
    """
    match_id = data.match_id
    winner_id = data.winner_id
    loser_id = data.loser_id

    global tournament_state
    bracket = tournament_state["bracket"]
    rounds = bracket["rounds"]
    losers_bracket = bracket["losers_bracket"]

    # Find the match in the main bracket
    match = None
    for round_matches in rounds:
        for m in round_matches:
            if m["match"] == match_id:
                match = m
                break
        if match:
            break

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    # Update match results
    match["winner"] = winner_id
    match["loser"] = loser_id

    # Update winners in subsequent rounds
    for round_matches in rounds:
        for m in round_matches:
            if m["team1"] == f"Winner of Match {match_id}":
                m["team1"] = {"id": winner_id, "name": f"Team {winner_id}"}
            if m["team2"] == f"Winner of Match {match_id}":
                m["team2"] = {"id": winner_id, "name": f"Team {winner_id}"}

    # Update losers in the losers' bracket
    for consolation_round in losers_bracket:
        for m in consolation_round:
            if m["team1"] == f"Loser of Match {match_id}":
                m["team1"] = {"id": loser_id, "name": f"Team {loser_id}"}
            if m["team2"] == f"Loser of Match {match_id}":
                m["team2"] = {"id": loser_id, "name": f"Team {loser_id}"}

    return bracket


@router.get("/tournament/bracket", tags=['tournament_new'])
def get_bracket() -> Dict:
    """
    Get the current state of the tournament bracket.
    """
    global tournament_state
    print(tournament_state)
    return tournament_state['bracket']
