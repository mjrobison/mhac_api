from sqlalchemy import Column, String
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric

from sqlalchemy.sql import text # type: ignore
from typing import TypedDict, List, Dict, Any, Optional
from uuid import uuid4, UUID
# from sqlalchemy.dialects.postgresql import JSON, UUID
from datetime import date, timedelta, datetime
from database import db

from .standings import add_to_standings, remove_from_standings

DB = db()

class Game(TypedDict):
    game_id =  Optional[UUID]
    home_team = UUID
    away_team = UUID
    final_home_score = Optional[int]
    final_away_score = Optional[int]

class GameResult(TypedDict):
    game_id = UUID
    period = int
    home_score = int
    away_score = int
    game_order = int

class Schedule(Game):
    game_date = date
    game_time = datetime
    season = dict
    neutral_site = bool

def get(game_id) -> Game:
    DB = db()
    stmt = text('''SELECT * FROM mhac.games WHERE game_id = :game_id ''')
    stmt = stmt.bindparams(game_id = game_id)
    results = DB.execute(stmt)
    DB.close()
    return results.fetchone()

def create(game: Schedule):
    # Check for active season?
    
    DB = db()
    game_id = uuid4()
    stmt = text('''INSERT INTO mhac.games(game_id, home_team_id, away_team_id) VALUES (:game_id, :home_team, :away_team) ''')
    stmt = stmt.bindparams(game_id = game_id , home_team = game.home_team, away_team=game.away_team)
    DB.execute(stmt)
        
    stmt = text('''INSERT INTO mhac.schedule (game_id, game_date, game_time, season_id, neutral_site) 
                   VALUES
                   (:game_id, :game_date, :game_time, :season_id, :neutral_site) ''')

    stmt = stmt.bindparams(game_id = game_id , game_date = game.game_date, game_time=game.game_time, season_id= game.season, neutral_site=game.neutral_site)
    DB.execute(stmt)
    DB.commit()
    DB.close()

    return {200: "success"}

def get_list():
    pass

def update(game: Schedule):
    #TODO: This Call isn't correct yet
    DB = db()
    game_id = game.game_id
    stmt = text('''INSERT INTO mhac.games(game_id, home_team_id, away_team_id) VALUES (:game_id, :home_team, :away_team) ''')
    stmt = stmt.bindparams(game_id = game_id , home_team = game.home_team, away_team=game.away_team)
    DB.execute(stmt)

def add_period_score(game: GameResult):
    #Game Order is for display purposes since it built the possibility of OT to be OT1, OT2, OT3. It is the actual period number
    period = game.period
    if period > 4:
        period = 'OT ' + game.period - 4

    DB = db()
    stmt = text('''INSERT INTO mhac.games_results(game_id, period, home_score, away_score, game_order) 
                VALUES 
                (:game_id, :period, :home_score,:away_score, :game_order) ''')
    stmt = stmt.bindparams(game_id = game.game_id , period=game.period, home_score=game.home_score, away_score=game.away_score, game_order=game.period)
    DB.execute(stmt)
    DB.commit()
    return {200: "Success"}

def add_final_score(game: Game):
    update_standings = False
    #Add a validator for the verification
    DB = db()

    #Start with verifying the period score
    stmt = text('''SELECT * FROM mhac.game_results WHERE game_id = :game_id ''')
    stmt = stmt.bindparams(game_id = game.game_id)
    results = DB.execute(stmt)
    
    if results.rowcount > 0:
        home_score = 0
        away_score = 0
        for result in results:
            home_score += result.home_score
            away_score += result.away_score
            
        if home_score != game.final_home_score or away_score != game.final_away_score:
            return {400, "final scores dont match the period score"}
    
    
    stmt = text('''SELECT * FROM mhac.games where game_id =:game_id ''')
    stmt = stmt.bindparams(game_id = game.game_id)
    results = DB.execute(stmt)
    game_score = results.fetchone()

    if (game.final_home_score and game.final_away_score) and (not game_score.final_home_score or not game_score.final_away_score):
        update_standings = True
    elif game_score.final_home_score and game_score.final_away_score:
        if game_score.final_home_score > game_score.final_away_score and game.final_home_score < game.final_away_score:
            # Reverse game Standings
            remove_from_standings(game.home_team, game_score.final_home_score > game_score.final_away_score, DB)
            remove_from_standings(game.away_team, game_score.final_home_score < game_score.final_away_score, DB)
            update_standings = True
            DB.commit()


    stmt = text('''UPDATE mhac.games
                   SET final_home_score = :final_home_score, final_away_score = :final_away_score
                   WHERE game_id = :game_id''')
    stmt = stmt.bindparams(game_id = game.game_id , final_home_score = game.final_home_score, final_away_score=game.final_away_score)
    DB.execute(stmt)
    DB.commit()

    if update_standings:
        #Takes a season team id
        add_to_standings(game.home_team, event=game.final_home_score > game.final_away_score, database=DB)
        add_to_standings(game.away_team, event=game.final_home_score < game.final_away_score, database=DB)
        DB.commit()

    DB.close()
    return {200: "success"}

def update_period_score(game: GameResult):
    #TODO: Check the score difference and send back a positive or negative
    pass

def get_game_results(game_id: UUID, team_id: UUID):
    #TODO: GameId, TeamID, Final Scores, Player Stats 
    pass
    DB = db()
    team_roster = text('''SELECT * FROM  ''')
