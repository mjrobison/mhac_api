from fastapi import HTTPException

from sqlalchemy import Column, String
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric

from sqlalchemy.sql import text  # type: ignore
from typing import TypedDict, List, Dict, Any, Optional
from uuid import uuid4, UUID

from datetime import date, timedelta, datetime, time
from database import db
import csv

from .seasons import get_by_id, Season
from .teams import get_with_uuid, TeamOut

import json


class MatchUp(TypedDict):
    team1: Optional[str]
    scoreTeam1: Optional[int]
    team1Seed: Optional[int]
    team2: Optional[str]
    scoreTeam2: Optional[int]
    team2seed: Optional[int]
    winner_to: Optional[str]
    loser_to: Optional[str]


class Location(TypedDict):
    address: str
    name: str


class TournamentGame(TypedDict):
    game: int
    date: date
    time: time
    matchup: MatchUp
    location: Location
    seasons: Season
    game_description: str


def tournamentGameRowMapper(row) -> TournamentGame:
    TournamentGame = {
        'logical_game_number': row['logical_game_number'],
        'game': row['game_number'],
        'date': row['game_date'],
        'time': row['game_time'],
        'game_description': row['game_description'],
        'display': row['display'],
        'matchup': {
            'team1': get_with_uuid(row['home_team'])['team_name'] if row['home_team'] else None,
            'scoreTeam1': row['home_team_score'],
            'team1Seed': row['home_team_seed'],
            'team2': get_with_uuid(row['away_team'])['team_name'] if row['away_team'] else None,
            'scoreTeam2': row['away_team_score'],
            'team2Seed': row['away_team_seed'],
            'winners_from': row['winners_from'],
            'losers_from': row['losers_from'],
            'winner_to': row['winner_to'],
            'loser_to': row['loser_to']
        },
        'location': {
            'address': '',
            'name': ''
        },
        'seasons': get_by_id(row['season_id'])
    }
    return TournamentGame


def tournamentRowMapper(row):
    return {
        'tournament_id': row['tournament_id'],
        'season': get_by_id(row['tournament_season']),
        'year': row['tournament_year']
    }


def get_tournament_games(season_id=None) -> TournamentGame:
    if season_id:
        where = f'WHERE seasons.id = :season_id '
    else:
        season_id = '2021'
        where = 'WHERE year = :season_id'

    query = text(f'''
    SELECT ROW_NUMBER() OVER (PARTITION BY seasons.id ORDER BY game_date, game_time ) AS logical_game_number, game_number, game_date, game_time, home_team.team_id as home_team
    , away_team.team_id as away_team, home_team_score, away_team_score, '' as game_location
    , seasons.id as season_id,
    home_team_seed, away_team_seed, 
        (SELECT string_agg(game_number::text, ',')
    FROM mhac.tournamentgames t
    WHERE winner_to = tournamentgames.game_number
    AND season_id = tournamentgames.season_id) AS winners_from,   
    (SELECT string_agg(game_number::text, ',')
    FROM mhac.tournamentgames t
    WHERE loser_to = tournamentgames.game_number
        AND season_id = tournamentgames.season_id) AS losers_from
    , tournamentgames.game_description
    , CASE WHEN seasons.tournament_start_date > current_date + 3 THEN false
        ELSE true
    END display, 
    winner_to, loser_to
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

    {where}
    ORDER BY game_number
    ''')

    query = query.bindparams(season_id=season_id)

    data_all = []
    with db() as DB:
        results = DB.execute(query)
        for r in results:
            data_all.append(tournamentGameRowMapper(r))
    
    return data_all


def get_tournament(year=None):
    query = """SELECT * FROM mhac.tournaments"""
    data_all = []
    with db() as DB:
        results = DB.execute(query)
        for r in results:
            data_all.append(tournamentRowMapper(r))

    return data_all


def create_tournament_game(game):
    next_game = game.game
    with db() as DB:
        if game.game is None:
            query = text("""SELECT MAX(game_number) + 1 FROM mhac.tournamentgames WHERE season_id = :season_id """)
            query = query.bindparams(season_id=game.season_id)
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
            query = query.bindparams(game_number=next_game, game_date=game.date, game_time=game.time,
                                    home_team_seed=game.matchup.team1Seed, away_team_seed=game.matchup.team2Seed,
                                    game_description=game.game_description, season_id=game.seasons.season_id,
                                    winner_to=game.matchup.winner_to, loser_to=game.matchup.loser_to)

            
            DB.execute(query)
            DB.commit()
        except Exception as exc:
            print(str(exc))
            DB.rollback()
            raise

    return {'success': 200}


def update_tournament_game(game):
    update_query = text("""UPDATE mhac.tournamentgames 
        SET home_team_seed = :home_team_seed, away_team_seed = :away_team_seed
        WHERE game_number = :game_number 
            AND season_id = :season_id """)

    try:
        # Check for scores
        if game.matchup.scoreTeam1 is not None and game.matchup.scoreTeam2 is not None:

            # Declare a variable for the winner and loser of the game
            if game.matchup.scoreTeam1 > game.matchup.scoreTeam2:
                winner = game.matchup.team1Seed
                loser = game.matchup.team2Seed
            else:
                winner = game.matchup.team2Seed
                loser = game.matchup.team1Seed

            # Update the game scores if they are there.
            update = text("""UPDATE mhac.tournamentgames 
            SET home_team_score = :home_team_score, away_team_score = :away_team_score
            WHERE game_number = :game_number AND season_id = :season_id """)

            update = update.bindparams(home_team_score=game.matchup.scoreTeam1, away_team_score=game.matchup.scoreTeam2,
                                       game_number=game.game, season_id=game.seasons.season_id)
            with db() as DB:
                DB.execute(update)
                DB.commit()

                # Check for where to place the winner/loser from the game
                game_query = text(
                    """SELECT * FROM mhac.tournamentgames WHERE game_number = :game_number and season_id = :season_id""")
                game_query = game_query.bindparams(game_number=game.game, season_id=game.seasons.season_id)
                result = DB.execute(game_query).fetchone()

                return_object = {}
                print(f"Original Game information {result}")

                # Winner Update
                if result.winner_to is not None:

                    # If the winner needs to added to another game, find the game 
                    game_query = game_query.bindparams(game_number=result.winner_to, season_id=result.season_id)
                    winner_game = DB.execute(game_query).fetchone()
                    update_home = ''
                    update_away = ''

                    # The logic below was a little confusing for me: 
                    # First you have to determine if the "winner_to" game already has a team associated with it, if there is no team, add the team to the home slot
                    # Next, if there is a team determine if that team is from the game just updated if it is replace it
                    # Else, if the team currently in the home slot isn't part of the game just updated determine if the winner is a higher or lower seed
                    # If lower push into home, else push into away
                    # Thirdly. If both seeds are populated, figure out which on contains the seed from the game just updated. then determine the new lower seed 
                    # based off of the new winner and the previously added winner

                    # Does this game have a location to push a winner to?
                    if winner_game:
                        # Does the game currently have a team in the home_seed
                        if winner_game.home_team_seed:
                            # Determine if the updated game has any seedings already in the winner game home or away slots
                            if (winner_game['home_team_seed'] or winner_game['away_team_seed']) and any(
                                    seeding in [int(winner_game['home_team_seed']),
                                                int(winner_game['away_team_seed']) if winner_game.away_team_seed else None]
                                    for seeding in [int(result['home_team_seed']), int(result['away_team_seed'])]):
                                # If the winner of this game is already present then we need to do nothing here otherwise we need to add the winner to the game
                                if winner not in [int(winner_game['home_team_seed']), int(
                                        winner_game['away_team_seed']) if winner_game.away_team_seed else None]:

                                    # Was home team of the "winner" game, part of the updated game
                                    # if so update the home team, keeping the away team 
                                    if winner_game['home_team_seed'] in [result['home_team_seed'],
                                                                        result['away_team_seed']]:
                                        if winner_game.away_team_seed:
                                            # determine which of the two teams is the lower seed
                                            # Lower seed becomes the home team
                                            if winner < int(winner_game.away_team_seed):
                                                update_home = winner
                                                update_away = winner_game.away_team_seed
                                            else:
                                                update_home = winner_game.away_team_seed
                                                update_away = winner
                                        else:
                                            update_home = winner
                                            update_away = winner_game.away_team_seed

                                    # Was away team of the "winner" game, part of the updated game
                                    # If so update the away team keeping the home team 
                                    if winner_game.away_team_seed in [result['home_team_seed'], result['away_team_seed']]:
                                        # determine which of the two teams is the lower seed
                                        # Lower seed becomes the home team
                                        if winner < int(winner_game.home_team_seed):
                                            update_home = winner
                                            update_away = winner_game.home_team_seed
                                        else:
                                            update_home = winner_game.home_team_seed
                                            update_away = winner
                            else:
                                if winner < int(winner_game.home_team_seed):
                                    update_home = winner
                                    update_away = winner_game.home_team_seed
                                else:
                                    update_home = winner_game.home_team_seed
                                    update_away = winner

                        else:
                            update_home = winner
                            update_away = winner_game.away_team_seed

                    if update_home:
                        update_query = update_query.bindparams(home_team_seed=update_home, away_team_seed=update_away,
                                                            game_number=result.winner_to, season_id=result.season_id)

                        DB.execute(update_query)
                        DB.commit()

                # Loser Update
                if result.loser_to is not None:
                    game_query = game_query.bindparams(game_number=result.loser_to, season_id=result.season_id)

                    # If the winner needs to added to another game, find the game 
                    loser_game = DB.execute(game_query).fetchone()
                    update_home = ''
                    update_away = ''

                    if loser_game:
                        print(loser_game)
                        if loser_game.home_team_seed:
                            print("Here1")
                            if (loser_game['home_team_seed'] or loser_game['away_team_seed']) and any(
                                    seeding in [int(loser_game['home_team_seed']),
                                                int(loser_game['away_team_seed']) if loser_game.away_team_seed else None]
                                    for seeding in [int(result['home_team_seed']), int(result['away_team_seed'])]):
                                print("Here2")
                                if loser not in [int(loser_game['home_team_seed']),
                                                int(loser_game['away_team_seed']) if loser_game.away_team_seed else None]:
                                    print("here3")
                                    if loser_game['home_team_seed'] in [result['home_team_seed'], result['away_team_seed']]:
                                        print("Here4")
                                        if loser_game.away_team_seed:
                                            print("HEre5")
                                            # determine which of the two teams is the lower seed
                                            # Lower seed becomes the home team
                                            if loser < int(loser_game.away_team_seed):
                                                update_home = loser
                                                update_away = loser_game.away_team_seed
                                            else:
                                                update_home = loser_game.away_team_seed
                                                update_away = loser
                                        else:
                                            update_home = loser
                                            update_away = loser_game.away_team_seed

                                    # Was away team of the "winner" game, part of the updated game
                                    # If so update the away team keeping the home team 
                                    if loser_game.away_team_seed in [result['home_team_seed'], result['away_team_seed']]:
                                        print("Here7")
                                        # determine which of the two teams is the lower seed
                                        # Lower seed becomes the home team
                                        if loser < int(loser_game.home_team_seed):
                                            update_home = loser
                                            update_away = loser_game.home_team_seed
                                        else:
                                            update_home = loser_game.home_team_seed
                                            update_away = loser
                            else:
                                if loser < int(loser_game.home_team_seed):
                                    update_home = loser
                                    update_away = loser_game.home_team_seed
                                else:
                                    update_home = loser_game.home_team_seed
                                    update_away = loser

                        else:
                            update_home = loser
                            update_away = loser_game.away_team_seed

                    if update_home:
                        update_query = update_query.bindparams(home_team_seed=update_home, away_team_seed=update_away,
                                                            game_number=result.loser_to, season_id=result.season_id)

                        DB.execute(update_query)
                        DB.commit()



        # What about reordering games
        else:
            query = text(""" 
                UPDATE mhac.tournamentgames
                SET game_date = :game_date, game_time = :game_time, home_team_seed = :home_team_seed, away_team_seed = :away_team_seed, game_description = :game_description, winner_to = :winner_to, loser_to = :loser_to
                WHERE game_number = :game_number
                    AND season_id = :season_id
            """)
            query = query.bindparams(season_id=game.seasons.season_id, game_number=game.game, game_date=game.date,
                                     game_time=game.time, home_team_seed=game.matchup.team1Seed,
                                     away_team_seed=game.matchup.team2Seed, game_description=game.game_description,
                                     winner_to=game.matchup.winner_to, loser_to=game.matchup.loser_to)
            with db() as DB:
                DB.execute(query)
                DB.commit()
    except Exception as exc:
        print(str(exc))
        raise HTTPException(status_code=400, detail=str(exc))
    return
