from sqlalchemy import Column, String
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric

from sqlalchemy.sql import text # type: ignore
from typing import TypedDict, List, Dict, Any, Optional
from uuid import uuid4, UUID

from datetime import date, timedelta, datetime, time
from database import db
import csv

from .seasons import get_by_id
from .teams import get_with_uuid, TeamOut

import json

class MatchUp(TypedDict):
    team1 = Optional[str]
    scoreTeam1 = Optional[int]
    team1Seed = Optional[int]
    team2 = Optional[str]
    scoreTeam2 = Optional[int]
    team2seed = Optional[int]
    winner_to = Optional[int]
    loser_to = Optional[int]

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
        'game_description': row['game_description'],
        'matchup': {
            'team1': get_with_uuid(row['home_team'])['team_name'] if row['home_team'] else None,
            'scoreTeam1': row['home_team_score'],
            'team1Seed': row['home_team_seed'],
            'team2': get_with_uuid(row['away_team'])['team_name'] if row['away_team'] else None,
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
    SELECT game_number, game_date, game_time, home_team.team_id as home_team
    , away_team.team_id as away_team, home_team_score, away_team_score, '' as game_location
    , levels.level_name as level_name,
    home_team_seed, away_team_seed, winner_to, loser_to
    , tournamentgames.game_description
    , home_team.*
    , away_team.*
    FROM mhac.tournamentgames
    INNER JOIN mhac.seasons
        ON tournamentgames.season_id = seasons.id
    INNER JOIN mhac.levels 
        ON levels.id = seasons.level_id
    LEFT OUTER JOIN mhac.standings as home_team
        ON tournamentgames.home_team_seed::int = home_team.standings_rank
        AND tournamentgames.season_id = home_team.season_id
    LEFT OUTER JOIN mhac.standings as away_team
        ON tournamentgames.away_team_seed::int = away_team.standings_rank
        AND tournamentgames.season_id = away_team.season_id
    -- LEFT OUTER JOIN mhac.season_teams_with_names as home_team_with_name
    --     ON home_team.team_id = home_team_with_name.id
    -- LEFT OUTER JOIN mhac.season_teams_with_names as away_team_with_name
    --     ON away_team.team_id = away_team_with_name.id
    
    WHERE year = '2020'
    ORDER BY game_number
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
        query = text("""SELECT MAX(game_number) + 1 FROM mhac.tournamentgames WHERE season_id = :season_id """)
        query = query.bindparams(season_id = game.season_id)
        next_game = DB.execute(query).fetchone()
        next_game = next_game[0]
        if next_game is None:
            next_game = 1
    
    if game.winners_from:
        if len(game.winners_from) > 2:
            return "too many past games", 400
        
        try:
            for past_game in game.winners_from:
                query = text(""" UPDATE mhac.tournamentgames
                SET winner_to = :game_number
                WHERE game_number = :past_game
                """)
                query = query.bindparams(game_number=next_game, past_game=past_game)
                DB.execute(query)
            DB.commit()
        except Exception as exc:
            print(str(exc))
            raise
            
    try:
        query = text("""
        INSERT INTO mhac.tournamentgames(game_number,  game_date, game_time, home_team_seed, away_team_seed, game_description, season_id, winner_to, loser_to)
        VALUES
        (:game_number, :game_date, :game_time, :home_team_seed, :away_team_seed, :game_description, :season_id, :winner_to, :loser_to)
        """)
        query = query.bindparams(game_number = next_game, game_date= game.game_date, game_time=game.game_time, home_team_seed = game.home_team_seed, away_team_seed = game.away_team_seed, 
                        game_description = game.game_description, season_id = game.season_id, winner_to = game.winner_to, loser_to = game.loser_to)

        DB.execute(query)
        DB.commit()
    except Exception as exc:
        print(str(exc))
        DB.rollback()
        raise
    
    return {'success': 200}

def update_tournament_game(game, DB=db()):
    if game.home_team_score is not None and game.away_team_score is not None:
        update = text("""UPDATE mhac.tournamentgames 
        SET home_team_score = :home_team_score, away_team_score = :away_team_score
        WHERE game_number = :game_number AND season_id = :season_id """)

        update = update.bindparams(home_team_score = game.home_team_score, away_team_score = game.away_team_score, game_number = game.game_number, season_id = game.season_id)

        DB.execute(update)
        DB.commit()

        game_query = text("""SELECT * FROM mhac.tournamentgames WHERE game_number = :game_number and season_id = :season_id""")

        game_query = game_query.bindparams(game_number = game.game_number, season_id = game.season_id)
        result = DB.execute(game_query).fetchone()
        # print(f'\n\n\n{result}\n\n{result.winner_to}')
        update_query = text("""UPDATE mhac.tournamentgames 
            SET home_team_seed = :home_team_seed, away_team_seed = :away_team_seed
            WHERE game_number = :game_number 
                AND season_id = :season_id """)

        # print(game.home_team_score, game.away_team_score, game.home_team_seed)
        if game.home_team_score > game.away_team_score:
            winner = game.home_team_seed
            loser = game.away_team_seed
        else:
            winner = game.away_team_seed
            loser = game.home_team_seed
        
        # Winner Update
        # Get the number game information

        game_query = game_query.bindparams(game_number=result.winner_to, season_id = result.season_id)
        winner_game = DB.execute(game_query).fetchone()
        
        if winner_game.home_team_seed is not None:
            # Determine the lower seed for home team
            if int(winner_game.home_team_seed) < int(winner):
                update_query = update_query.bindparams(home_team_seed = winner, away_team_seed = winner_game.home_team_seed, game_number = result.winner_to, season_id = result.season_id)
            else:
                update_query = update_query.bindparams(away_team_seed = winner, home_team_seed = winner_game.home_team_seed, game_number = result.winner_to, season_id = result.season_id)
        else:
           update_query = update_query.bindparams(home_team_seed = winner, away_team_seed = None, game_number = result.winner_to, season_id = result.season_id)
        
        
        DB.execute(update_query)
        DB.commit()
        
        game_query = game_query.bindparams(game_number=result.loser_to, season_id = result.season_id)
        loser_game = DB.execute(game_query).fetchone()
        
        if loser_game.home_team_seed is not None:
            # Determine the lower seed for home team
            if loser_game.home_team_seed < winner:
                new_update_query = update_query.bindparams(home_team_seed = loser, away_team_seed = loser_game.home_team_seed, game_number = result.loser_to, season_id = result.season_id)
            else:
                new_update_query = update_query.bindparams(away_team_seed = loser, home_team_seed = loser_game.home_team_seed, game_number = result.loser_to, season_id = result.season_id)
        else:
            new_update_query = update_query.bindparams(home_team_seed = loser, away_team_seed = None, game_number = result.loser_to, season_id = result.season_id)
        
        DB.execute(new_update_query)
        DB.commit()
        
        
    #What about reordering games

    query = """ 
        UPDATE mhac.tournamentgames
        SET game_date = :game_date, game_time = :game_time, home_team_seed = :home_team_seed, away_team_seed = :away_team_seed, game_description = :game_description, winner_to = :winner_to, loser_to = :loser_to
        WHERE game_number = :game_number
            AND season_id = :season_id
    """
    # query = query.bindparams(game_date = game.game_date, game_time = game.game_time, home_team_seed)