from sqlalchemy import Column, String
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric

from sqlalchemy.sql import text # type: ignore
from typing import TypedDict, List, Dict, Any, Optional
from uuid import uuid4, UUID

from datetime import date, timedelta, datetime, time
from database import db
import csv

from .seasons import get_by_id

import json

class MatchUp(TypedDict):
    team1 = str
    scoreTeam1 = int
    team2 = str
    scoreTeam2 = int

class Location(TypedDict):
    address = str
    name = str

class TournamentGame(TypedDict):
    game = int
    date = date
    time = time
    matchup = MatchUp
    location = Location
    level = str

def tournamentGameRowMapper(row) -> TournamentGame:
    TournamentGame = {
        'game': row['game_number'],
        'date': row['game_date'],
        'time': row['game_time'],
        'matchup': {
            'team1': row['home_team'],
            'scoreTeam1': row['home_team_score'],
            'team1Seed': row['home_team_seed'],
            'team2': row['away_team'],
            'scoreTeam2': row['away_team_score'],
            'team2Seed': row['away_team_seed'],
            'winner_to': row['winner_to'],
            'loser_to': row['loser_to']
        },
        'location': {
            'address': '',
            'name': ''
        },
        'level': row['level_name']
    }
    return TournamentGame

def tournamentRowMapper(row):
    return {
        'tournament_id': row['tournament_id'],
        'season': get_by_id(row['tournament_season']),
        'year': row['tournament_year']
    }


def get_tournament_games() -> TournamentGame:
    DB = db()
    query = '''
    SELECT game_number, game_date, game_time, home_team.team_name as home_team, away_team.team_name as away_team, home_team_score, away_team_score, '' as game_location
    , levels.level_name as level_name,
    home_team_seed, away_team_seed, winner_to, loser_to
    FROM mhac.tournamentgames
    INNER JOIN mhac.seasons
        ON tournamentgames.season_id = seasons.id
    INNER JOIN mhac.levels 
        ON levels.id = seasons.level_id
    INNER JOIN mhac.season_teams_with_names as home_team
        ON tournamentgames.home_team = home_team.id
    INNER JOIN mhac.season_teams_with_names as away_team
        ON tournamentgames.away_team = away_team.id
    WHERE year = '2020'
    '''
    
    data_all=[]
    results = DB.execute(query)
    for r in results:
        data_all.append(tournamentGameRowMapper(r))
        
    return data_all


def get_tournament(DB=db(), year=None):
    query = """SELECT * FROM mhac.tournaments"""
    data_all = []
    results = DB.execute(query)
    for r in results:
        data_all.append(tournamentRowMapper(r))
    
    return data_all

def create_tournament_game(game, DB=db()):
    next_game = game.game_number
    if game.game_number is None:
        query = """SELECT MAX(game_number) + 1 FROM mhac.tournamentgames WHERE season_id = :season_id """
        query.bindparams(season_id = game.season_id)
        DB.execute(query)
        next_game = DB.fetchone()

    try:
        query = """
        INSERT INTO mhac.tournamentgames(game_number,  game_date, game_time, home_team_seed, away_team_seed, game_description, season_id, winner_to, loser_to)
        VALUES
        (:game_number, :game_date, :game_time, :home_team_seed, :away_team_see, :description, :season_id, :winner_to, :loser_to)
        """
        query.bindparams(game_number = next_game, game_date= game.game_date, game_time=game.game_time, home_team_seed = game.home_team_seed, away_team_seed = game.away_team_seed, 
                        game_description = game.game_description, season_id = game.season.id, winner_to = game.winner_to, loser_to = game.loser_to)

        DB.execute(query)
    except Exception as exc:
        print(str(exc))
        DB.rollback()
        raise
    
    return {'success': 200}

def update_tournament_game(game, DB=db()):
    if game.home_team_score is not None and game.away_team_score is not None:
        #Begin Updating tournament
        # Start with pushing the seed numbers to the new game number
        # Do I need the team_name/ID?
        pass
    
    #What about reordering games
    
    query = """ 
        UPDATE mhac.tournamentgames
        SET game_date = :game_date, game_time = :game_time, home_team_seed = :home_team_seed, away_team_seed = :away_team_seed, game_description = :game_description, winner_to = :winner_to, loser_to = :loser_to
        WHERE game_number = :game_number
            AND season_id = :season_id
    """