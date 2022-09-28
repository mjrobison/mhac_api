from sqlalchemy import Column, String
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric

from sqlalchemy.sql import text # type: ignore
from typing import TypedDict, List, Dict, Any, Optional
from uuid import uuid4, UUID
# from sqlalchemy.dialects.postgresql import JSON, UUID
from datetime import date, timedelta, datetime
from database import db

from .standings import add_to_standings, remove_from_standings
from .teams import get_with_uuid as team_get

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

class final_scores(TypedDict):
    away_score: int
    home_score: int

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

# class GameResultsOut(TypedDict):
#     # final_scores: final_scores
#     # game_id: UUID
    
#     stats: List[Player]

def game_result_row_mapper(row) -> Player:
    Player = {'id': row['id'],
        'team': team_get(row['season_team_id']),
        'first_name': row['roster_first_name'],
        'last_name': row['roster_last_name'],
        'number': row['roster_number'],
        'person_type': '1',
        'player_stats': {
            'FGA': row['field_goals_attempted'],
            'FGM': row['field_goals_made'],
            'ThreePA': row['three_pointers_attempted'],
            'ThreePM': row['three_pointers_made'],
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

def get_game_results(game_id: UUID, team_id: UUID) -> List[Player]:
    #TODO: GameId, TeamID, Final Scores, Player Stats 

    print(game_id, team_id)
    DB = db()
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
    WHERE mhac.team_rosters.season_team_id = :team_id 
        AND mhac.games.game_id = :game_id 
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
    stmt = stmt.bindparams(team_id=team_id, game_id=game_id)
    
    query = DB.execute(stmt)

    DB.close()
    results = query.fetchall()
    player_list = []
    for row in results:
        player_list.append(game_result_row_mapper(row))
    return player_list

def get_team_games(season_id: UUID, slug:str):
    DB = db()
    stmt = text('''SELECT * 
    FROM mhac.schedule
    INNER JOIN mhac.games 
        ON schedule.game_id = games.game_id
    INNER JOIN mhac.season_teams_with_names as home_team
        ON schedule.season_id = home_team.season_id
        AND games.home_team_id = home_team.id
    INNER JOIN mhac.season_teams_with_names as away_team
        ON schedule.season_id = away_team.season_id
        AND games.away_team_id = away_team.id
    WHERE schedule.season_id = :season_id
        AND (home_team.slug = :team_slug
        OR away_team.slug = :team_slug)
    ''')

    stmt = stmt.bindparams(team_slug = sug, season_id=season_id)
    results = DB.execute(stmt)
    DB.close()
    return results


def get_program_schedule(slug: str):
    DB = db()
    stmt = text(""" 
    SELECT 
        mhac.schedule.id AS mhac_schedule_id
        , mhac.schedule.game_id AS mhac_schedule_game_id
        , mhac.schedule.game_date AS mhac_schedule_game_date
        , mhac.schedule.game_time AS mhac_schedule_game_time
        , mhac.schedule.season_id AS mhac_schedule_season_id
        , mhac.schedule.neutral_site AS mhac_schedule_neutral_site
        , mhac.games.game_id AS mhac_games_game_id
        , mhac.games.home_team_id AS mhac_games_home_team_id, mhac.games.away_team_id AS mhac_games_away_team_id, mhac.games.final_home_score AS mhac_games_final_home_score, mhac.games.final_away_score AS mhac_games_final_away_score, home_team.id AS home_team_id, home_team.season_id AS home_team_season_id, home_team.team_id AS home_team_team_id, home_team.team_name AS home_team_team_name, home_team.team_mascot AS home_team_team_mascot, home_team.address_id AS home_team_address_id, home_team.main_color AS home_team_main_color, home_team.secondary_color AS home_team_secondary_color, home_team.website AS home_team_website, home_team.logo_color AS home_team_logo_color, home_team.logo_grey AS home_team_logo_grey, home_team.slug AS home_team_slug, home_team.level_name AS home_team_level_name, away_team.id AS away_team_id, away_team.season_id AS away_team_season_id, away_team.team_id AS away_team_team_id, away_team.team_name AS away_team_team_name, away_team.team_mascot AS away_team_team_mascot, away_team.address_id AS away_team_address_id, away_team.main_color AS away_team_main_color, away_team.secondary_color AS away_team_secondary_color, away_team.website AS away_team_website, away_team.logo_color AS away_team_logo_color, away_team.logo_grey AS away_team_logo_grey, away_team.slug AS away_team_slug, away_team.level_name AS away_team_level_name, mhac.addresses.id AS mhac_addresses_id, mhac.addresses.name AS mhac_addresses_name, mhac.addresses.address_line_1 AS mhac_addresses_address_line_1, mhac.addresses.address_line_2 AS mhac_addresses_address_line_2, mhac.addresses.city AS mhac_addresses_city, mhac.addresses.state AS mhac_addresses_state, mhac.addresses.postal_code AS mhac_addresses_postal_code
    FROM mhac.games 
    JOIN mhac.schedule 
        ON mhac.games.game_id = mhac.schedule.game_id 
    JOIN mhac.season_teams_with_names AS home_team 
        ON mhac.games.home_team_id = home_team.id 
    JOIN mhac.season_teams_with_names AS away_team 
        ON mhac.games.away_team_id = away_team.id 
    JOIN mhac.addresses 
        ON home_team.address_id = mhac.addresses.id
    JOIN mhac.seasons
        ON mhac.schedule.season_id = mhac.seasons.id
    WHERE mhac.seasons.archive is null
    ORDER BY mhac.schedule.game_date
    """)
