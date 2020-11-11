from sqlalchemy import Column, String
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric

from sqlalchemy.sql import text # type: ignore
from typing import TypedDict, List, Dict, Any, Optional
from uuid import uuid4, UUID
# from sqlalchemy.dialects.postgresql import JSON, UUID
from datetime import date, timedelta, datetime, time
from database import db

from .standings import add_to_standings, remove_from_standings
from .teams import get_with_uuid as team_get, SeasonTeam

import json

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
    date = date
    time = time
    season = dict
    neutral_site = bool

class final_scores(TypedDict):
    away_score: Optional[int]
    home_score: Optional[int]

class PlayerStats(TypedDict):
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

class Player(TypedDict):
    first_name: str
    last_name: str
    id: UUID
    number: int
    player_stats: PlayerStats
    team: SeasonTeam

class TeamSchedule(TypedDict):
    schedule_id: int
    game_date: date
    game_time: time
    game_id: UUID
    home_team: SeasonTeam
    away_team: SeasonTeam
    final_scores: final_scores

    
def team_schedule_row_mapper(row) -> TeamSchedule:
    TeamSchedule = {
        'schedule_id': row['schedule_id'],
        'game_date': row['game_date'],
        'game_time': row['game_time'],
        'game_id': row['game_id'],
        'home_team': team_get(row['home_team']),
        'away_team': team_get(row['away_team']),
        'final_scores': {
            'away_score': row['final_away_score'],
            'home_score': row['final_home_score']
        }

    }
    return TeamSchedule

def game_result_row_mapper(row) -> Player:
    Player = {'player_id': row['id'],
        # 'team': team_get(row['season_team_id']),
        'player_first_name': row['roster_first_name'],
        'player_last_name': row['roster_last_name'],
        'player_number': row['roster_number'],
        'person_type': '1',
        'player_stats': {
            '2PA': row['field_goals_attempted'],
            '2PM': row['field_goals_made'],
            '3PA': row['three_pointers_attempted'],
            '3PM': row['three_pointers_made'],
            'FTA': row['free_throws_attempted'],
            'FTM': row['free_throws_made'],
            'total_points': row['total_points'],
            'AST': row['assists'],
            'assists': row['assists'],
            'STEAL': row['steals'],
            'steals': row['steals'],
            'BLK': row['blocks'],
            'blocks': row['blocks'],
            'OREB': row['offensive_rebounds'],
            'DREB': row['defensive_rebounds'],
            'offensive_rebounds': row['offensive_rebounds'],
            'defensive_rebounds': row['defensive_rebounds'],
            'TO': row['turnovers'],
            'total_rebounds': row['total_rebounds']
        }
    }
    return Player

def final_score_mapper(row):
    final_score = {
        'home_score': row['final_home_score'],
        'away_score': row['final_away_score']
    }
    return final_score
            
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

    stmt = stmt.bindparams(game_id = game_id, game_date = game.date, game_time=game.time, season_id= game.season, neutral_site=game.neutral_site)
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

    DB = db()
    stmt = text(''' 
        SELECT period as quarter, home_score, away_score FROM mhac.games_results where game_id = :game_id
    ''')
    stmt = stmt.bindparams(game_id = game_id)
    results = DB.execute(stmt)
    quarter_scores = {}
    for (quarter, home_score, away_score) in results:
        quarter_scores['quarter'] = quarter
        quarter_scores['home_score'] = home_score
        quarter_scores['away_score'] = away_score
    
    stmt = text(''' 
        SELECT * FROM mhac.games where game_id = :game_id
    ''')
    stmt = stmt.bindparams(game_id = game_id)
    results = DB.execute(stmt)

    game = {}
    game['game_id'] = game_id
    game['team_id'] = team_id
    game['final_scores'] = final_score_mapper(results.fetchone())

    stmt = text('''WITH game_roster AS
    (
        SELECT mhac.team_rosters.season_team_id AS season_team_id
        , mhac.person.id AS id
        , mhac.person.first_name AS first_name
        , mhac.person.last_name AS last_name
        , mhac.person.number AS number
        , mhac.games.game_id AS game_id
    FROM mhac.team_rosters 
    JOIN mhac.season_teams_with_names 
        ON mhac.team_rosters.season_team_id = mhac.season_teams_with_names.id 
    JOIN mhac.games 
        ON mhac.games.home_team_id = mhac.season_teams_with_names.id 
            OR mhac.games.away_team_id = mhac.season_teams_with_names.id 
    JOIN mhac.person ON mhac.person.id = mhac.team_rosters.player_id
    WHERE  mhac.games.game_id = :game_id 
        AND season_teams_with_names.id = :team_id
    )
    SELECT
        roster.season_team_id,
        roster.id AS id, 
        roster.first_name AS roster_first_name, 
        roster.last_name AS roster_last_name, 
        roster.number AS roster_number, 
        coalesce(mhac.basketball_stats.field_goals_made, 0) AS field_goals_made, 
        coalesce(mhac.basketball_stats.field_goals_attempted, 0) AS field_goals_attempted, 
        coalesce(mhac.basketball_stats.three_pointers_made, 0) AS three_pointers_made, 
        coalesce(mhac.basketball_stats.three_pointers_attempted, 0) AS three_pointers_attempted, 
        coalesce(mhac.basketball_stats.free_throws_made, 0) AS free_throws_made, 
        coalesce(mhac.basketball_stats.free_throws_attempted, 0) AS free_throws_attempted, 
        coalesce(mhac.basketball_stats.total_points, 0) AS total_points, 
        coalesce(mhac.basketball_stats.assists, 0) AS assists, 
        coalesce(mhac.basketball_stats.offensive_rebounds, 0) AS offensive_rebounds, 
        coalesce(mhac.basketball_stats.defensive_rebounds, 0) AS defensive_rebounds, 
        coalesce(mhac.basketball_stats.total_rebounds, 0) AS total_rebounds, 
        coalesce(mhac.basketball_stats.steals, 0) AS steals, 
        coalesce(mhac.basketball_stats.blocks, 0) AS blocks, 
        coalesce(mhac.basketball_stats.turnovers, 0) AS turnovers
    FROM game_roster AS roster 
    LEFT OUTER JOIN mhac.basketball_stats 
        ON roster.game_id = mhac.basketball_stats.game_id 
        AND roster.id = mhac.basketball_stats.player_id
    ''')
    stmt = stmt.bindparams(game_id=game_id, team_id = team_id)
    
    results = DB.execute(stmt)

    DB.close()
    # results = query.fetchall()
    player_list = []
    for row in results:
        player_list.append(game_result_row_mapper(row))
    game['player_stats'] = player_list
    print(game)
    return game

def get_team_schedule(season_team_id: UUID = None, season_id: UUID = None, slug: str = None) -> List[TeamSchedule]:
    DB = db()
    base_query = text('''SELECT
         schedule.id as schedule_id, 
            games.game_id as game_id,
            schedule.game_date as game_date,
            schedule.game_time as game_time, 
            home_team.id as home_team,
            away_team.id as away_team, 
            final_home_score, 
            final_away_score  
        FROM mhac.games
        INNER JOIN mhac.schedule 
            ON games.game_id = schedule.game_id
        LEFT OUTER JOIN mhac.season_teams_with_names AS home_team
            ON games.home_team_id = home_team.id
        LEFT OUTER JOIN mhac.season_teams_with_names AS away_team
            ON games.away_team_id = away_team.id''')
    
    if not season_team_id: 
        stmt = text(f''' {base_query}
            WHERE (home_team.slug = :slug
                OR away_team.slug = :slug)
                AND schedule.season_id = :season_id ''')
        stmt = stmt.bindparams(slug = slug, season_id = season_id)
    else:
        stmt = text(f''' {base_query}
            WHERE (home_team.id = :season_team_id
                OR away_team.id = :season_team_id)''')
        stmt = stmt.bindparams(season_team_id = season_team_id)
    # print(stmt)
    results = DB.execute(stmt)
    DB.close()
    schedule = []
    for game in results:
        # print(team_schedule_row_mapper(game))
        schedule.append(team_schedule_row_mapper(game))
    # print(json.dumps(dict(schedule), indent=4))
    return schedule