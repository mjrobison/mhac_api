from sqlalchemy import Column, String
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric

from sqlalchemy.sql import text # type: ignore
from typing import TypedDict, List, Dict, Any, Optional
from uuid import uuid4, UUID
# from sqlalchemy.dialects.postgresql import JSON, UUID
from datetime import date, timedelta, datetime, time
from database import db
import csv

from .standings import add_to_standings, remove_from_standings
from .teams import get_with_uuid as team_get, SeasonTeam

import json

from sqlalchemy.dialects import postgresql

DB = db()

schedule_base_query = text('''SELECT
         schedule.id as schedule_id, 
            games.game_id as game_id,
            schedule.game_date as game_date,
            schedule.game_time as game_time, 
            home_team.id as home_team,
            away_team.id as away_team, 
            final_home_score, 
            final_away_score,
            CASE WHEN(SELECT count(*) FROM mhac.basketball_stats 
                INNER JOIN mhac.season_teams_with_names 
                    ON basketball_stats.team_id = season_teams_with_names.id
                    AND season_teams_with_names.slug = :slug
                AND basketball_stats.game_id = games.game_id) = 0 THEN true ELSE false 
            END as missing_stats  
        FROM mhac.games
        INNER JOIN mhac.schedule 
            ON games.game_id = schedule.game_id
        LEFT OUTER JOIN mhac.season_teams_with_names AS home_team
            ON games.home_team_id = home_team.id
        LEFT OUTER JOIN mhac.season_teams_with_names AS away_team
            ON games.away_team_id = away_team.id
        ''')

class Game(TypedDict):
    game_id =  Optional[UUID]
    home_team = UUID
    away_team = UUID
    final_home_score = Optional[int]
    final_away_score = Optional[int]

class GameResult(TypedDict):
    game_id = Optional[UUID]
    period = str
    home_score = Optional[int]
    away_score = Optional[int]
    game_order = Optional[int]

class Schedule(Game):
    date = date
    time = time
    season = dict
    neutral_site = bool

class final_scores(TypedDict):
    away_score: Optional[int]
    home_score: Optional[int]

class PlayerStats(TypedDict):
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
    missing_stats: Optional[bool]

class GameIdDel(TypedDict):
    game_id: UUID

class GameStats(TypedDict):
    game_id: UUID
    team_id: UUID
    game_scores: Optional[List[GameResult]]
    final_scores: final_scores
    player_stats: PlayerStats
    
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
        },
        'missing_stats': row['missing_stats']

    }
    return TeamSchedule

def game_result_row_mapper(row) -> Player:
    Player = {'player_id': row['id'],
        'player_first_name': row['roster_first_name'],
        'player_last_name': row['roster_last_name'],
        'player_number': row['roster_number'],
        'person_type': '1',
        'player_stats': {
            'game_played': row['game_played'],
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

def add_period_score(game: GameResult, game_id: UUID, database=None):
    #Game Order is for display purposes since it built the possibility of OT to be OT1, OT2, OT3. It is the actual period number
    if database is None:
        DB = db()
    else:
        DB = database

    num_period = len(game)
    if num_period > 4:
        period = 'OT-' + str(num_period - 4)

    for score in game:
        
        i = 1
        stmt = text('''INSERT INTO mhac.game_results(game_id, period, home_score, away_score, game_order) 
                    VALUES 
                    (:game_id, :period, :home_score,:away_score, :game_order) ''')
        stmt = stmt.bindparams(game_id=game_id , period=score.period, home_score=score.home_score, away_score=score.away_score, game_order=i)
        DB.execute(stmt)
        i += 1 
    if database is None:
        DB.commit()
        return {200: "Success"}

def add_final_score(game: GameStats, connection=None):
    
    update_standings = False
    #Add a validator for the verification
    if not connection:
        DB = db()
    else:
        DB = connection

    #Start with verifying the period score
    stmt = text('''SELECT * FROM mhac.game_results WHERE game_id = :game_id ''')
    stmt = stmt.bindparams(game_id = game.game_id)
    results = DB.execute(stmt)
    # print(results, results.rowcount, str(results))
    if results.rowcount > 0:
        home_score = 0
        away_score = 0
        for result in results:
            home_score += result.home_score or 0
            away_score += result.away_score or 0 
            
        if home_score != game.final_scores.home_score or away_score != game.final_scores.away_score:
            return {400, "final scores dont match the period score"}
    
    
    stmt = text('''SELECT * FROM mhac.games where game_id =:game_id ''')
    stmt = stmt.bindparams(game_id = game.game_id)
    results = DB.execute(stmt)
    game_score = results.fetchone()
    
    if (game.final_scores.home_score and game.final_scores.away_score) and (not game_score.final_home_score or not game_score.final_away_score):
        update_standings = True
    elif game_score.final_home_score and game_score.final_away_score:
        # print("here")
        if (game_score.final_home_score > game_score.final_away_score and game.final_scores.home_score < game.final_scores.away_score) or (game_score.final_home_score < game_score.final_away_score and game.final_scores.home_score > game.final_scores.away_score):
            # Reverse game Standings
            remove_from_standings(game_score.home_team_id, game_score.final_home_score > game_score.final_away_score, DB)
            remove_from_standings(game_score.away_team_id, game_score.final_home_score < game_score.final_away_score, DB)
            update_standings = True
            DB.commit()


    stmt = text('''UPDATE mhac.games
                   SET final_home_score = :final_home_score, final_away_score = :final_away_score
                   WHERE game_id = :game_id''')
    stmt = stmt.bindparams(game_id = game.game_id , final_home_score = game.final_scores.home_score, final_away_score=game.final_scores.away_score)
    DB.execute(stmt)
    if not connection:
        DB.commit()

    if update_standings:
        #Takes a season team id
        add_to_standings(game_score.home_team_id, event=game.final_scores.home_score > game.final_scores.away_score, database=DB)
        add_to_standings(game_score.away_team_id, event=game.final_scores.home_score < game.final_scores.away_score, database=DB)
        if not connection:
            DB.commit()
    
    if not connection:
        DB.close()
        return {200: "success"}

def update_period_score(game: GameResult, game_id, database=None):
    #TODO: Check the score difference and send back a positive or negative
    for score in game:
        print(score)

def get_game_results(game_id: UUID, team_id: UUID):
    #TODO: GameId, TeamID, Final Scores, Player Stats 
    # print(game_id, team_id)
    DB = db()
    stmt = text(''' 
        SELECT COALESCE(expected_periods.period, game_results.period) as quarter, home_score, away_score, game_order 
        FROM mhac.game_results 
        FULL OUTER JOIN (
            SELECT '1' AS period, :game_id AS game_id
            UNION
            SELECT '2' AS period, :game_id AS game_id
            UNION
            SELECT '3' AS period, :game_id AS game_id
            UNION
            SELECT '4' AS period, :game_id AS game_id
            
        ) as expected_periods
            ON game_results.game_id = expected_periods.game_id
            AND game_results.period = expected_periods.period
        where (expected_periods.game_id = :game_id
        OR game_results.game_id = :game_id)
        ORDER BY game_order

    ''')
    stmt = stmt.bindparams(game_id = game_id)
    results = DB.execute(stmt)
    game_scores = []
    for (quarter, home_score, away_score, game_order) in results:
        quarter_scores = {}

        quarter_scores['game_id'] = game_id
        quarter_scores['period'] = quarter
        quarter_scores['home_score'] = home_score
        quarter_scores['away_score'] = away_score
        quarter_scores['game_order'] = game_order
        game_scores.append(quarter_scores)

    stmt = text(''' 
        SELECT * FROM mhac.games where game_id = :game_id
    ''')
    stmt = stmt.bindparams(game_id = game_id)
    results = DB.execute(stmt)

    game = {}
    game['game_id'] = game_id
    game['final_scores'] = final_score_mapper(results.fetchone())
    game['game_scores'] = game_scores

    team_filter = ''
    if team_id:
        team_filter = 'AND season_teams_with_names.id = :team_id'
    game['team_id'] = team_id
    stmt = text(f'''WITH game_roster AS
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
        {team_filter}
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
        coalesce(mhac.basketball_stats.turnovers, 0) AS turnovers,
        coalesce(mhac.basketball_stats.game_played, false) AS game_played
    FROM game_roster AS roster 
    LEFT OUTER JOIN mhac.basketball_stats 
        ON roster.game_id = mhac.basketball_stats.game_id 
        AND roster.id = mhac.basketball_stats.player_id
    ''')
    if team_id:
        stmt = stmt.bindparams(game_id=game_id, team_id=team_id)
    else:
        stmt = stmt.bindparams(game_id=game_id)
    # print(stmt)
    results = DB.execute(stmt)

    DB.close()

    player_list = []
    for row in results:
        player_list.append(game_result_row_mapper(row))
    game['player_stats'] = player_list
    
    return game

def get_team_schedule(season_team_id: UUID = None, season_id: UUID = None, slug: str = None) -> List[TeamSchedule]:
    DB = db()
    missing_subquery = ''
    wheres = ''

    if season_id and slug: 
        missing_subquery = text ('''SELECT count(*) FROM mhac.basketball_stats 
                INNER JOIN mhac.season_teams_with_names 
                    ON basketball_stats.team_id = season_teams_with_names.id
                    AND season_teams_with_names.slug = :slug
                    AND basketball_stats.game_id = games.game_id
                    and season_teams_with_names.season_id = :season_id
                ''')
                
        wheres = text(''' 
            WHERE (home_team.slug = :slug
                OR away_team.slug = :slug)
                AND schedule.season_id = :season_id ''')

        stmt = text(f'''SELECT
            schedule.id as schedule_id, 
                games.game_id as game_id,
                schedule.game_date as game_date,
                schedule.game_time as game_time, 
                home_team.id as home_team,
                away_team.id as away_team, 
                final_home_score, 
                final_away_score,
                CASE WHEN ({missing_subquery}) = 0 THEN true ELSE false END as missing_stats
            FROM mhac.games
            INNER JOIN mhac.schedule 
                ON games.game_id = schedule.game_id
            LEFT OUTER JOIN mhac.season_teams_with_names AS home_team
                ON games.home_team_id = home_team.id
            LEFT OUTER JOIN mhac.season_teams_with_names AS away_team
                ON games.away_team_id = away_team.id
            {wheres}
            ORDER BY schedule.game_date
            ''')
        stmt = stmt.bindparams(slug = slug, season_id = season_id)
    
    elif season_team_id :
        missing_subquery = text ('''SELECT count(*) FROM mhac.basketball_stats 
                INNER JOIN mhac.season_teams_with_names 
                    ON basketball_stats.team_id = season_teams_with_names.id
                    AND season_teams_with_names.id = :season_team_id
                    AND basketball_stats.game_id = games.game_id
                ''')

        wheres = text(f''' 
            WHERE (home_team.id = :season_team_id
                OR away_team.id = :season_team_id)''')
        
        stmt = text(f'''SELECT
            schedule.id as schedule_id, 
                games.game_id as game_id,
                schedule.game_date as game_date,
                schedule.game_time as game_time, 
                home_team.id as home_team,
                away_team.id as away_team, 
                final_home_score, 
                final_away_score,
                CASE WHEN ({missing_subquery}) = 0 THEN true ELSE false END as missing_stats
            FROM mhac.games
            INNER JOIN mhac.schedule 
                ON games.game_id = schedule.game_id
            LEFT OUTER JOIN mhac.season_teams_with_names AS home_team
                ON games.home_team_id = home_team.id
            LEFT OUTER JOIN mhac.season_teams_with_names AS away_team
                ON games.away_team_id = away_team.id
            {wheres}
            ORDER BY schedule.game_date
            ''')
        stmt = stmt.bindparams(season_team_id = season_team_id)
    
    else :
        missing_subquery = '0' 
        #  text('''SELECT count(*), season_team_id FROM mhac.basketball_stats 
        #         INNER JOIN mhac.season_teams_with_names 
        #             ON basketball_stats.team_id = season_teams_with_names.id
        #             AND basketball_stats.game_id = games.game_id
        #         ''')
        
        stmt = text(f'''SELECT
            schedule.id as schedule_id, 
                games.game_id as game_id,
                schedule.game_date as game_date,
                schedule.game_time as game_time, 
                home_team.id as home_team,
                away_team.id as away_team, 
                final_home_score, 
                final_away_score,
                CASE WHEN ({missing_subquery}) = 0 THEN true ELSE false END as missing_stats
            FROM mhac.games
            INNER JOIN mhac.schedule 
                ON games.game_id = schedule.game_id
            LEFT OUTER JOIN mhac.season_teams_with_names AS home_team
                ON games.home_team_id = home_team.id
            LEFT OUTER JOIN mhac.season_teams_with_names AS away_team
                ON games.away_team_id = away_team.id
            WHERE (home_team.archive is null and away_team.archive is null)
            ORDER BY schedule.game_date
            ''')
        # stmt = stmt.bindparams()
    # print(stmt)

    results = DB.execute(stmt)
    DB.close()
    schedule = []
    for game in results:
        schedule.append(team_schedule_row_mapper(game))
    # print(schedule)
    return schedule

def get_program_schedule(slug: str = None, year=None) -> List[TeamSchedule]:
    DB = db()
    
    stmt = text(f''' {schedule_base_query}
            WHERE home_team.archive is null and away_team.archive is null
             AND (home_team.slug = :slug
                OR away_team.slug = :slug)
            ''')
    stmt = stmt.bindparams(slug = slug)
    
    results = DB.execute(stmt)
    DB.close()
    schedule = []
    for game in results:
        schedule.append(team_schedule_row_mapper(game))
    return schedule

def get_season_schedule(season_id):
    DB = db()
    
    stmt = text(f''' {schedule_base_query}
            WHERE season_id = :season_id
            ''')

    missing_subquery = text ('''SELECT count(*) FROM mhac.basketball_stats 
            INNER JOIN mhac.season_teams_with_names 
                ON basketball_stats.team_id = season_teams_with_names.id
                AND basketball_stats.game_id = games.game_id
                and season_teams_with_names.season_id = :season_id
            ''')
            
    wheres = text(''' 
        WHERE schedule.season_id = :season_id ''')

    stmt = text(f'''SELECT
        schedule.id as schedule_id, 
            games.game_id as game_id,
            schedule.game_date as game_date,
            schedule.game_time as game_time, 
            home_team.id as home_team,
            away_team.id as away_team, 
            final_home_score, 
            final_away_score,
            CASE WHEN ({missing_subquery}) = 0 THEN true ELSE false END as missing_stats
        FROM mhac.games
        INNER JOIN mhac.schedule 
            ON games.game_id = schedule.game_id
        LEFT OUTER JOIN mhac.season_teams_with_names AS home_team
            ON games.home_team_id = home_team.id
        LEFT OUTER JOIN mhac.season_teams_with_names AS away_team
            ON games.away_team_id = away_team.id
        {wheres}
        ''')

    # stmt = stmt.bindparams(slug = slug, season_id = season_id)
    stmt = stmt.bindparams(season_id = season_id)
    
    results = DB.execute(stmt)
    DB.close()
    schedule = []
    for game in results:
        schedule.append(team_schedule_row_mapper(game))
    return schedule

def remove_game(game: GameIdDel):
    try:
        DB = db()
        stmt = text("""
        SELECT * FROM mhac.game_results WHERE game_id = :game_id
        """)
        stmt = stmt.bindparams(game_id = game.game_id)
        results = DB.execute(stmt)

        if results.rowcount > 0:
            return {400: "Game has results attached"}


        stmt = text("""
        DELETE FROM mhac.schedule WHERE game_id = :game_id
        """)
        stmt = stmt.bindparams(game_id = game.game_id)
        DB.execute(stmt)
        DB.commit()

        stmt = text("""
        DELETE FROM mhac.games WHERE game_id = :game_id
        """)
        stmt = stmt.bindparams(game_id = game.game_id)
        DB.execute(stmt)
        DB.commit()
    except Exception as exc:
        print(str(exc))
        return {404: 'Game not found'}
    finally:
        DB.close()

def parse_csv(fileContents, game_id, team_id):
    
    DB = db()
    insert_stmt = text(""" 
    INSERT INTO mhac.basketball_stats(game_id,player_id,game_played,field_goals_attempted,field_goals_made,three_pointers_attempted,three_pointers_made,free_throws_attempted,free_throws_made,total_points,assists,offensive_rebounds,defensive_rebounds,total_rebounds,steals,blocks,team_id,turnovers,roster_id)
    VALUES
    (:game_id,:player_id,true, :field_goals_attempted,:field_goals_made,:three_pointers_attempted,:three_pointers_made,:free_throws_attempted,:free_throws_made,:total_points,:assists,:offensive_rebounds,:defensive_rebounds,:total_rebounds,:steals,:blocks,:team_id,:turnovers,:roster_id )
    """)
    index = 0 
    headers = []
    stats = []
    players_not_in_roster = []
    team_sum = 0
    records = fileContents.decode('utf-8').split('\r\n')
    for record in records:
        # print(record)
        if len(record) < 2:
            continue
        line = dict(zip(headers, record.split('|')))
        # print(line)
        if index <= 1:
            headers = record.split('|')
        else:
            stmt = text("""SELECT * FROM mhac.team_rosters
                INNER JOIN mhac.person  
                    on team_rosters.player_id = person.id
                WHERE season_team_id = :team_id
                and person.number= :jersey  """)
            stmt = stmt.bindparams(team_id=team_id, jersey=line['Jersey'])
            results = DB.execute(stmt)
            player = results.fetchone()
            
            if player:
                
                insert_stmt = insert_stmt.bindparams(game_id=game_id, 
                                                    player_id = player['player_id'], 
                                                    field_goals_attempted=line['TwoPointAttempts'],
                                                    field_goals_made=line['TwoPointsMade'],
                                                    three_pointers_attempted=line['ThreePointAttempts'],
                                                    three_pointers_made=line['ThreePointsMade'],
                                                    free_throws_attempted=line['FreeThrowAttempts'],
                                                    free_throws_made=line['FreeThrowsMade'],
                                                    total_points=line['Points'],
                                                    assists=line['Assists'],
                                                    offensive_rebounds=line['OffensiveRebounds'],
                                                    defensive_rebounds=line['DefensiveRebounds'],
                                                    total_rebounds=line['Rebounds'],
                                                    steals=line['Steals'],
                                                    blocks=line['BlockedShots'],
                                                    team_id=team_id,
                                                    turnovers=line['Turnovers'],
                                                    roster_id = player['roster_id']
                                                    )
                # print("insert stmt", insert_stmt.compile(dialect=postgresql.dialect()))
                DB.execute(insert_stmt)
            else:
                players_not_in_roster.append(line['Jersey'])
            
        index += 1 
    
    if len(players_not_in_roster)>0:
        DB.rollback()
        # print( {'missing_players': players_not_in_roster})
        
        return {'missing_players': players_not_in_roster}
    else:
        DB.commit()
    return {200: "success"}

def add_stats(player_stats, game_id, team_id, connection=None): 
    
    if not connection:
        DB = db()
    else: 
        DB = connection
    
    insert_stmt = text(""" 
    INSERT INTO mhac.basketball_stats(game_id,player_id,game_played, field_goals_attempted,field_goals_made,three_pointers_attempted,three_pointers_made,free_throws_attempted,free_throws_made,total_points,assists,offensive_rebounds,defensive_rebounds,total_rebounds,steals,blocks,team_id,turnovers,roster_id)
    VALUES
    (:game_id,:player_id,:game_played, :field_goals_attempted,:field_goals_made,:three_pointers_attempted,:three_pointers_made,:free_throws_attempted,:free_throws_made,:total_points,:assists,:offensive_rebounds,:defensive_rebounds,:total_rebounds,:steals,:blocks,:team_id,:turnovers,:roster_id )
    ON CONFLICT ON CONSTRAINT ux_stats
    DO
    UPDATE 
    SET 
    game_id = :game_id,
    game_played = :game_played,
    field_goals_attempted = :field_goals_attempted,
    field_goals_made=:field_goals_made,
    three_pointers_attempted =:three_pointers_attempted,
    three_pointers_made=:three_pointers_made,
    free_throws_attempted= :free_throws_attempted,
    free_throws_made =:free_throws_made,
    total_points = :total_points,
    assists=:assists,
    offensive_rebounds=:offensive_rebounds,
    defensive_rebounds=:defensive_rebounds,
    total_rebounds=:total_rebounds,
    steals=:steals,
    blocks=:blocks,
    turnovers=:turnovers
    """)

    try:
        for line in player_stats:
            # print(line)
            stmt = text("""SELECT * FROM mhac.team_rosters
                    INNER JOIN mhac.person  
                        on team_rosters.player_id = person.id
                    WHERE season_team_id = :team_id
                    and player_id = :player_id  """)
            stmt = stmt.bindparams(team_id=team_id, player_id=line.player_id)
            results = DB.execute(stmt)
            player = results.fetchone()

            insert_stmt = insert_stmt.bindparams(game_id=game_id, 
                                                player_id = player.player_id, 
                                                field_goals_attempted=line.FGA,
                                                field_goals_made=line.FGM,
                                                three_pointers_attempted=line.ThreePA,
                                                three_pointers_made=line.ThreePM,
                                                free_throws_attempted=line.FTA,
                                                free_throws_made=line.FTM,
                                                total_points=line.total_points,
                                                assists=line.AST,
                                                offensive_rebounds=line.OREB,
                                                defensive_rebounds=line.DREB,
                                                total_rebounds=line.total_rebounds,
                                                steals=line.steals,
                                                blocks=line.blocks,
                                                team_id=team_id,
                                                turnovers=line.TO,
                                                roster_id = player.roster_id,
                                                game_played = line.game_played
                                                )

            DB.execute(insert_stmt)
            if not connection:
                DB.commit()
    except Exception as exc:
        print(str(exc))
    finally:
        if not connection:
            DB.close()
    return "200"

def add_games_and_stats(game: GameStats):
    print('entrypoint')
    game_id = game.game_id
    team_id = game.team_id
    DB = db()
    
    add_period_score(game.game_scores, game_id, database=DB)
    add_stats(game.player_stats, game_id, team_id)
    print("final_Scores", game.final_scores)
    final_scores = game.final_scores

    if final_scores.home_score or final_scores.away_score:
        add_final_score(game, DB)
    try:
        DB.commit()
    except Exception as exc:
        print(str(exc))
    finally:
        DB.close()

def stats_by_season_and_team(season_id, team_id):
    DB = db()
    base_query = text("""SELECT 
    st.season_id, player_id, number AS player_number, bs.team_id, p.first_name, p.last_name, t.team_name
                , SUM(field_goals_attempted) AS field_goals_attempted
                , SUM(field_goals_made) AS field_goals_made
                , SUM(three_pointers_attempted) AS three_pointers_attempted
                , SUM(three_pointers_made) AS three_pointers_made
                , SUM(free_throws_attempted) AS free_throws_attempted
                , SUM(free_throws_made) AS free_throws_made
                , SUM(total_points) AS total_points
                , SUM(assists) AS assists
                , SUM(offensive_rebounds) AS offensive_rebounds
                , SUM(defensive_rebounds) AS defensive_rebounds
                , SUM(total_rebounds) AS total_rebounds
                , SUM(steals) AS steals
                , SUM(blocks) AS blocks
                , SUM(turnovers) AS turnovers
                , COUNT(game_id) AS games_played
            FROM mhac.basketball_stats aS bs
            INNER JOIN mhac.season_teams AS st
                ON bs.team_id = st.id
            INNER JOIN mhac.teams AS t
                ON st.team_id = t.id
            INNER JOIN mhac.person AS p
                ON bs.player_id = p.id
            
    """)
    group_by = """GROUP BY st.season_id, player_id, bs.team_id, p.first_name, p.last_name, t.team_name, number"""
     
    if season_id and team_id:
        where = '''WHERE st.season_id = :season_id and st.id = :team_id '''
        stmt = text(f'''{base_query} 
                       {where} 
                       {group_by} ''')
        stmt = stmt.bindparams(season_id=season_id, team_id = team_id)               
        
    elif season_id:
        where = '''WHERE st.season_id = :season_id '''
        stmt = text(f'''{base_query} 
                       {where} 
                       {group_by} ''')
        stmt = stmt.bindparams(team_id=team_id)               

    elif team_id:
        where = ''' WHERE st.id = :team_id'''
        stmt = text(f'''{base_query} 
                       {where} 
                       {group_by} ''')
        stmt = stmt.bindparams(team_id = team_id)

    results = DB.execute(stmt)

    stats = {}
    stats['season_id'] = season_id
    stats['team_id'] = team_id
    data_all = []
    for r in results:
        field_goal_percentage = 0.0
∑<        if r.field_goals_attempted != 0:
            field_goal_percentage = float(r.field_goals_made)/float(r.field_goals_attempted)

        three_point_percentage = 0.0
        if r.three_pointers_attempted != 0:
            three_point_percentage = float(r.three_pointers_made)/float(r.three_pointers_attempted)

        free_throw_percentage = 0.0
        if r.free_throws_attempted != 0:
            free_throw_percentage = float(r.free_throws_made)/float(r.free_throws_attempted)
        data = {
            "team_id": r.team_id,
            "team_name": r.team_name,
            "player_first_name": r.first_name,
            "player_last_name": r.last_name,
            "player_number": r.player_number,
            "player_id": r.player_id,
            "player_stats": {
                "2PA": r.field_goals_attempted,
                "2PM": r.field_goals_made,
                '2P%': field_goal_percentage,
                "3PA": r.three_pointers_attempted,
                "3PM": r.three_pointers_made,
                "3P%": three_point_percentage, 
                "FTA": r.free_throws_attempted,
                "FTM": r.free_throws_made,
                "FT%": free_throw_percentage, 
                "total_points": r.total_points,
                "assists": r.assists,
                "offensive_rebounds": r.offensive_rebounds,
                "defensive_rebounds": r.defensive_rebounds,
                "total_rebounds": r.total_rebounds,
                "steals": r.steals,
                "blocks": r.blocks,
                "turnovers": r.turnovers,
                "games_played": r.games_played,
                "points_per_game": float(r.total_points)/float(r.games_played)
            }
        }
        data_all.append(data)
