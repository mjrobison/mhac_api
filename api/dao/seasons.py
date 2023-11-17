from sqlalchemy.sql import text  # type: ignore
from typing import TypedDict, List, Optional, Dict
from uuid import uuid4, UUID
from datetime import date
from database import db

from .levels import get_level_by_id, Level
from .teams import TeamOut, admin_get_with_uuid

class Season(TypedDict):
    level: Dict
    season_name:  str
    season_start_date: date
    roster_submission_deadline: date
    tournament_start_date: date
    sport: str
    year:  str
    archive: bool
    slug: Optional[str]


class SeasonIn(Season):
    season_id: Optional[UUID]


class SeasonUpdate(TypedDict):
    season_id: UUID
    season_name: str
    season_start_date: Optional[date]
    roster_submission_deadline: Optional[date]
    tournament_start_date: Optional[date]
    sport: str
    year: str
    archive: Optional[bool]
    slug: Optional[str]
    level: Level
    season_teams: Optional[List[TeamOut]]


class SeasonNew(TypedDict):
    level: List[Level]
    season_name:  str
    season_start_date: date
    roster_submission_deadline: date
    tournament_start_date: date
    sport: str
    year:  str
    archive: bool
    slug: Optional[str]
    season_teams: Optional[List[TeamOut]]


def row_mapper(row) -> Season:
    Season = {
        'season_id': row['season_id'],
        'level': row['level_name'],
        'season_name': row['name'],
        'season_start_date': row['start_date'],
        'roster_submission_deadline': row['roster_submission_deadline'],
        'tournament_start_date': row['tournament_start_date'],
        'sport': row['sport_name'],
        'year': row['year'],
        'slug': row['slug'],
        'archive': row['archive'] or False

    }
    return Season


def admin_season_row_mapper(row):
    season_teams = []
    if row.season_teams:
        season_teams = [admin_get_with_uuid(i) for i in row.season_teams.split(',')]
    
    Season = {
        'season_id': row['season_id'],
        'season_name': row['name'],
        'season_start_date': row['start_date'],
        'roster_submission_deadline': row['roster_submission_deadline'],
        'tournament_start_date': row['tournament_start_date'],
        'sport': row['sport_name'],
        'year': row['year'],
        'slug': row['slug'],
        'level': get_level_by_id(row['level_id']),
        'archive': row['archive'] or False,
        'season_teams': season_teams
    }
    
    return Season


base_query = '''
            SELECT seasons.id as season_id, 
            seasons.name, 
            seasons.start_date::date, 
            seasons.roster_submission_deadline::date, 
            seasons.tournament_start_date::date,
            sports.sport_name, 
            seasons.slug, 
            levels.level_name,
            levels.id as level_id, 
            seasons.year,
            seasons.archive
            FROM mhac.seasons 
            INNER JOIN mhac.levels 
                ON seasons.level_id = levels.id 
            INNER JOIN mhac.sports 
                ON seasons.sport_id = sports.id
        '''


def get_list(active=None, session=db()) -> List[Season]:
    season_list = []
    where = ''
    if active:
        where = 'WHERE archive is null'
    stmt = text(f'''{base_query} {where} ''')
    with db() as conn:
        result = conn.execute(stmt).mappings().all()

        for row in result:
            season_list.append(row_mapper(row))
    
    return season_list


def get(slug: str) -> Season:
    where = 'WHERE slug = :slug'
    stmt = text(F'''{base_query} {where} ''')
    
    with db() as session:
        result = session.execute(stmt.bindparams(slug=slug))
        season = row_mapper(result.mappings().one())
    
    return season


def get_by_id(id: UUID,) -> Season:
    where = 'WHERE seasons.id = :id'
    stmt = text(F'''{base_query} {where} ''')
    with db() as session:
        result = session.execute(stmt.bindparams(id=id))
        season = row_mapper(result.mappings().one())
    
    return season


def get_by_year(year: str) -> List[Season]:
    where = 'WHERE seasons.year = :year'
    stmt = text(F'''{base_query} {where} ''')
    with db() as session:
        result = session.execute(stmt.bindparams(year=year)).mappings().all()
        season_list = []
        for r in result:
            season_list.append(row_mapper(r))

    return season_list

def get_by_year_and_level(year:str, level_name:str):
    where = 'WHERE seasons.year = :year and lower(level_name) = :level_name'
    stmt = text(F'''{base_query} {where} ''')
    with db() as session:
        result = session.execute(stmt.bindparams(year=year, level_name=level_name)).mappings().one()
        
    return row_mapper(result)

def archive_season(season: UUID, session=db()):
    stmt = text(f'''UPDATE mhac.seasons
                     SET archive = True 
                     WHERE id = season_id ''')
    stmt = stmt.bindparams(season_id=season)

    session.execute(stmt)
    session.commit()
    session.close()
    return {200: "Season Archived"}


def remove_team_by_id(team_id: UUID, season_id: UUID, session=db()):
    #TODO: REFACTOR
    stmt = text(""" 
    DELETE FROM mhac.basketball_stats 
    WHERE game_id IN (SELECT game_id 
                      FROM mhac.games where home_team_id = :team_id 
                            or away_team_id = :team_id
                     );
    """)
    stmt = stmt.bindparams(team_id = team_id)
    session.execute(stmt)

    stmt = text(""" 
    DELETE FROM mhac.game_results 
    WHERE game_id IN (SELECT game_id FROM mhac.games where home_team_id = :team_id or away_team_id =:team_id);
    """)
    stmt = stmt.bindparams(team_id = team_id)
    session.execute(stmt)

    stmt = text(""" 
    DELETE FROM mhac.schedule 
    WHERE game_id IN (SELECT game_id FROM mhac.games where home_team_id = :team_id or away_team_id =:team_id);
    """)
    stmt = stmt.bindparams(team_id = team_id)
    session.execute(stmt)

    stmt= text(""" 
    DELETE FROM mhac.games where where home_team_id = :team_id or away_team_id = :team_id);
    """)

    stmt = text(""" 
        DELETE FROM mhac.standings
        WHERE season_id = :season_id
            AND team_id = :team_id
    """)
    stmt = stmt.bindparams(season_id = season_id, team_id = team_id)
    session.execute(stmt)

    stmt = text("""
        DELETE FROM mhac.season_teams 
        WHERE season_id = :season_id and team_id = :team_id
     """)
    stmt = stmt.bindparams(season_id = season_id, team_id = team_id)
    session.execute(stmt)

def add_team_to_season(season_id: UUID, team_id: UUID, session=None):
    season_team_id=uuid4()

    stmt = text("""INSERT INTO mhac.season_teams(id, season_id, team_id)
            VALUES
            (:id, :season_id, :team_id)
            """)
            
    stmt = stmt.bindparams(id=season_team_id, season_id=season_id, team_id=team_id)
    # with db() as session:
    try:
        session.execute(stmt)
        stmt = text('''INSERT INTO mhac.standings (team_id, season_id, wins, losses, games_played, win_percentage, standings_rank)
                    VALUES
            (:team_id, :season_id, 0, 0, 0, 0.00, 0) 
            ''')

        stmt = stmt.bindparams(team_id=season_team_id, season_id=season_id)
        session.execute(stmt)

    except Exception as exc:
        print(str(exc))
        raise exc



def update(season: SeasonUpdate):
    archive = season.archive
    if not season.archive:
        archive = None
    stmt = text('''UPDATE mhac.seasons
                  SET name = :name, 
                      start_date= :start_date, 
                      roster_submission_deadline= :roster_submission_deadline, 
                      tournament_start_date= :tournament_start_date,
                      archive = :archive,
                      slug = :slug 
                  WHERE id = :season_id''')
    stmt = stmt.bindparams(name=season.season_name,
                           start_date=season.season_start_date,
                           roster_submission_deadline=season.roster_submission_deadline,
                           tournament_start_date=season.tournament_start_date,
                           archive=archive,
                           slug=season.slug,
                           season_id=season.season_id)
    try:
        with db() as session:
            session.execute(stmt)
            stmt = text('''SELECT * FROM mhac.season_teams WHERE season_id = :season_id''')
            stmt = stmt.bindparams(season_id = season.season_id)
            current_season_teams = session.execute(stmt).mappings().all()
            # print(current_season_teams)
            current_team_list = [team['team_id'] for team in current_season_teams]
            incoming_team_list = [team['team_id'] for team in season.season_teams]
            teams_to_remove = set(current_team_list) - set(incoming_team_list)
            
            for team in teams_to_remove:
                remove_team_by_id(team_id= team, season_id=season.season_id, session=session)
            
            for team in season.season_teams:
                print(f'In team loop: {team}')
                if team['team_id'] in current_team_list:
                    continue
                add_team_to_season(season_id=season.season_id, team_id=team['team_id'], session=session)
                
            session.commit()
    except Exception as exc:
        print(str(exc))
        raise exc
    
    return {200: "Success"}


def create(season: SeasonNew, level: Level):
    print(season)
    new_season_id = uuid4()
    slug = season.slug
    return_statement = {}
    if season.slug == '' or not season.slug:
        slug = f"{season.year}_{str(level.level_name).lower()}_basketball"
    stmt = text('''INSERT INTO mhac.seasons(id, name, year, level_id, sport_id, start_date, roster_submission_deadline, tournament_start_date, archive, slug)
                VALUES
                (:id, :name, :year, :level, :sport, :season_start_date, :roster_submission_deadline, :tournament_start_date, :archive, :slug )''')
    
    stmt = stmt.bindparams(id=new_season_id, name=season.season_name, year=season.year, level=level.id,
                               sport=1, season_start_date=season.season_start_date,
                               roster_submission_deadline=season.roster_submission_deadline,
                               tournament_start_date=season.tournament_start_date, archive=None, slug=slug)
    try:
        with db() as session:
            result = session.execute(stmt)
        
            for team in season.season_teams:
                add_team_to_season(season_id=new_season_id, team_id= team.team_id, session=session)
            
            session.commit()
        return_statement = {200: f'{new_season_id} Added'}
    except Exception as exc:
        print(str(exc))

    return return_statement


def get_active_year(archive=None):
    stmt = text('''
        SELECT DISTINCT name, year 
        FROM mhac.seasons
        WHERE archive is NULL
        ORDER BY year desc
    ''')

    with db() as session:
        result = session.execute(stmt).mappings().one()
    

    return result


def get_all_years():
    stmt = text('''
        SELECT DISTINCT name, year 
        FROM mhac.seasons
        ORDER BY year desc
    ''')
    with db() as session:
        results = session.execute(stmt).mappings().all()
    
    return results

def get_admin_season():
    seasons = []
    stmt = text(''' 
    SELECT 
   		seasons.id::TEXT as season_id, 
        seasons.name, 
        seasons.start_date::date, 
        seasons.roster_submission_deadline::date, 
        seasons.tournament_start_date::date,
        sports.sport_name, 
        seasons.slug::TEXT as slug,
        levels.id::TEXT as level_id, 
        seasons.year,
        seasons.archive,
        string_agg(season_teams_with_names.id::text, ',') AS season_teams
    FROM mhac.seasons 
    INNER JOIN mhac.levels 
        ON seasons.level_id = levels.id 
    INNER JOIN mhac.sports 
        ON seasons.sport_id = sports.id
    LEFT OUTER JOIN mhac.season_teams_with_names
        ON seasons.id = season_teams_with_names.season_id
    GROUP BY seasons.id, seasons.name, seasons.start_date, seasons.tournament_start_date,
            seasons.roster_submission_deadline, sports.sport_name, seasons.year, seasons.slug,
            levels.id, seasons.archive
    ORDER BY seasons.year desc, levels.id
    ''')
    with db() as conn:
        results = conn.execute(stmt).mappings().all()
    
    for row in results:
        seasons.append(admin_season_row_mapper(row))
    return seasons

