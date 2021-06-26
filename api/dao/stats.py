from sqlalchemy import Column, String
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric

from sqlalchemy.sql import text # type: ignore
from typing import TypedDict, List, Dict, Any
from uuid import uuid4
from sqlalchemy.dialects.postgresql import JSON, UUID

from database import db

def game_result_row_mapper(row):
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

def stats_by_season_and_team(season_id, team_id):
    DB = db()
    data_all= []
    base_query = text("""SELECT st.season_id, player_id, number AS player_number, bs.team_id, p.first_name, p.last_name, t.team_name
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
            FROM mhac.basketball_stats AS bs
            INNER JOIN mhac.season_teams AS st
                ON bs.team_id = st.id
            INNER JOIN mhac.teams AS t
                ON st.team_id = t.id
            INNER JOIN mhac.person AS p
                ON bs.player_id = p.id
            WHERE bs.game_played = true
    """)
    group_by = """GROUP BY st.season_id, player_id, bs.team_id, p.first_name, p.last_name, t.team_name, number"""
    stmt = text(f"""{base_query}{group_by}""")
    if season_id and team_id:
        where = ''' AND st.season_id = :season_id AND st.id = :team_id '''
        stmt = text(f'''{base_query}
                       {where}
                       {group_by} ''')
        stmt = stmt.bindparams(season_id=season_id, team_id=team_id)
    elif season_id:
        where = '''AND st.season_id = :season_id '''
        stmt = text(f'''{base_query} 
                       {where} 
                       {group_by} ''')
        stmt = stmt.bindparams(season_id=season_id)               

    elif team_id:
        where = ''' AND st.id = :team_id'''
        stmt = text(f'''{base_query} 
                       {where} 
                       {group_by} ''')
        stmt = stmt.bindparams(team_id = team_id)

    results = DB.execute(stmt)

    stats = {}
    stats['season_id'] = season_id
    stats['team_id'] = team_id

    for r in results:
        field_goal_percentage = 0.0
        if r.field_goals_attempted != 0:
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
                "FGA": r.field_goals_attempted,
                "FGM": r.field_goals_made,
                '2P%': field_goal_percentage,
                "ThreePA": r.three_pointers_attempted,
                "ThreePM": r.three_pointers_made,
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
    return data_all


