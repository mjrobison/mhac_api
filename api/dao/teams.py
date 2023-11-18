from sqlalchemy.sql import text  # type: ignore
from typing import TypedDict, List, Dict, Any, Optional
from uuid import uuid4, UUID

from .addresses import get_address_with_id, Address
from database import db


class Team(TypedDict):
    team_name: str
    team_mascot: str
    main_color: str
    secondary_color: str
    website: Optional[str]
    logo_color: str
    logo_grey: str
    slug: str


class TeamOut(Team):
    team_id: UUID
    address: Optional[Address]
    season_id: Optional[UUID]


class SeasonTeam(Team):
    team_id: UUID
    season_id: UUID
    level_name: Optional[str]
    # select_team_name: Optional[str]


class SeasonTeamUpdate(Team):
    team_id: UUID
    season_id: Optional[UUID]
    address: Optional[Address]
    level_name: Optional[str]


def row_mapper(row) -> TeamOut:
    Team = {
        "team_id": row["id"],
        "team_name": row["team_name"],
        "team_mascot": row["team_mascot"],
        "main_color": row["main_color"],
        "secondary_color": row["secondary_color"],
        "website": row["website"],
        "logo_color": row["logo_color"],
        "logo_grey": row["logo_grey"],
        "slug": row["slug"],
        "address": get_address_with_id(row["address_id"]),
    }
    return Team


def season_team_row_mapper(row) -> SeasonTeam:
    SeasonTeam = {
        "team_id": row["id"],
        # 'team_name': row['team_name'],
        "team_mascot": row["team_mascot"],
        "main_color": row["main_color"],
        "secondary_color": row["secondary_color"],
        "website": row["website"],
        "logo_color": row["logo_color"],
        "logo_grey": row["logo_grey"],
        "slug": row["slug"],
        "season_id": row["season_id"],
        "level_name": row["level_name"],
        "team_name": row["team_name"],
    }
    return SeasonTeam


def row_mapper_team(row) -> TeamOut:
    Team = {
        "team_id": row["team_id"],
        "team_name": row["team_name"],
        "team_mascot": row["team_mascot"],
        "main_color": row["main_color"],
        "secondary_color": row["secondary_color"],
        "website": row["website"],
        "logo_color": row["logo_color"],
        "logo_grey": row["logo_grey"],
        "slug": row["slug"],
        "address": get_address_with_id(row["address_id"]),
    }
    return Team

def season_team_level_row_mapper(row) -> SeasonTeam:
    SeasonTeam = {
        "team_id": row["id"],
        # 'team_name': row['team_name'],
        "team_mascot": row["team_mascot"],
        "main_color": row["main_color"],
        "secondary_color": row["secondary_color"],
        "website": row["website"],
        "logo_color": row["logo_color"],
        "logo_grey": row["logo_grey"],
        "slug": row["slug"],
        "season_id": row["season_id"],
        "level_name": row["level_name"],
        "team_name": row["team_name"],
    }
    return SeasonTeam


def get(slug: str) -> List[Team]:
    team_list = []
    stmt = text(
        """SELECT * FROM mhac.season_teams_with_names WHERE slug = :slug and archive is null"""
    )
    stmt = stmt.bindparams(slug=slug)
    
    with db() as session:
        result = session.execute(stmt).mappings().all()
        for row in result:
            team_list.append(row_mapper(row))

    return team_list


def get_with_level_uuid(id: UUID) -> SeasonTeam:
    stmt = text("""SELECT * FROM mhac.season_teams_with_names WHERE id = :id""")
    stmt = stmt.bindparams(id=id)
    # print(stmt)
    with db() as session:
        result = session.execute(stmt)
        row = result.mappings().one()

    if row is None:
        raise LookupError(f"Could not find key value with id: {id}")

    key = season_team_level_row_mapper(row)
    return key


def get_season_teams(slug: str = None) -> List[SeasonTeam]:
    team_list = []

    base_query = text(
        f"""SELECT * FROM mhac.season_teams_with_names 
        WHERE archive is null"""
    )

    with db() as session:
        if not slug:
            query = base_query
        elif type(slug) == UUID:
            query = text(f"""{base_query}  AND season_id = :slug """)
            query = query.bindparams(slug=slug)
        else:
            query = text(f""" {base_query} AND slug = :slug """)
            query = query.bindparams(slug=slug)

        result = session.execute(query)
        results_as_dict = result.mappings().all()
        for row in results_as_dict:
            team_list.append(season_team_row_mapper(row))

    return team_list


def get_season_team(slug: str, seasonid: str) -> SeasonTeam:
    team_list = []

    stmt = text(
        """SELECT * FROM mhac.season_teams_with_names WHERE slug = :slug and archive is null and season_id = :seasonid"""
    )
    stmt = stmt.bindparams(slug=slug, seasonid=seasonid)

    with db() as session:
        resultset = session.execute(stmt)
        result = season_team_row_mapper(resultset.mappings().one())
    return result


def get_list() -> List[TeamOut]:
    team_list = []
    stmt = text("""SELECT * FROM mhac.teams WHERE active""")
    with db() as session:
        result = session.execute(stmt).mappings().all()

        for row in result:
            team_list.append(row_mapper(row))

    return team_list


def get_with_uuid(id: UUID) -> SeasonTeam:
    stmt = text("""SELECT * FROM mhac.season_teams_with_names WHERE id = :id""")
    stmt = stmt.bindparams(id=id)
    with db() as session:
        result = session.execute(stmt)
        row = result.mappings().one()

    if row is None:
        raise LookupError(f"Could not find key value with id: {id}")

    key = season_team_row_mapper(row)
    return key


def admin_get_with_uuid(id: UUID) -> SeasonTeam:
    stmt = text("""SELECT * FROM mhac.season_teams_with_names WHERE id = :id""")
    stmt = stmt.bindparams(id=id)

    with db() as session:
        result = session.execute(stmt)
        row = result.mappings().one()

    if row is None:
        raise LookupError(f"Could not find key value with id: {id}")

    key = row_mapper_team(row)
    return key


def create(team: Team):
    stmt = text(
        """INSERT INTO mhac.teams (id,team_name,team_mascot,address_id,main_color,secondary_color,website,logo_color,logo_grey,slug)
                   VALUES
                    (id,:team_name,:team_mascot,:address_id,:main_color,:secondary_color,:website,:logo_color,:logo_grey,:slug)"""
    )
    stmt = stmt.bindparams(
        id=uuid4,
        team_name=team.team_name,
        team_mascot=team.team_mascot,
        address_id="",
        main_color=team.main_color,
        secondary_color=team.secondary_color,
        website=team.website,
        logo_color=team.logo_color,
        logo_grey=team.logo_grey,
        slug=team.slug,
    )

    with db() as session:
        results = session.execute(stmt)
        session.commit()

    return results


def add_to_season(season_team: SeasonTeam):
    print(f"HERE: {season_team}")

    stmt = text(
        """INSERT INTO mhac.season_teams (id, season_id, team_id)
                   VALUES
                    (:id, :season_id, :team_id)"""
    )
    stmt = stmt.bindparams(
        id=uuid4, season_id=season_team.season_id, team_id=season_team.team_id
    )
    with db() as session:
        try:
            session.execute(stmt)
            stmt = text(
                """INSERT INTO mhac.standings (team_id, season_id, wins, losses, games_played, win_percentage, standings_rank)
            VALUES
            (:team_id, :season_id, 0, 0, 0, 0.00, 0) 
            """
            )
            stmt = stmt.bindparams(
                team_id=season_team.team_id, season_id=season_team.season_id
            )
            session.execute(stmt)
            session.commit()
        except:
            session.rollback()
            raise

    return "Team was successfully added to season"


def get_team_count(season_id=None):
    query = text(
        """SELECT COUNT(*) FROM mhac.season_teams_with_names INNER JOIN mhac.standings ON season_teams_with_names.id = standings.team_id WHERE season_teams_with_names.season_id = :season_id AND standings_rank <> 99"""
    )
    query = query.bindparams(season_id=season_id)

    with db() as session:
        results = session.execute(query).fetchone()
        results = results[0]

    return results


def get_with_slug(team_slug):
    stmt = text("""SELECT * FROM mhac.teams WHERE slug = :slug""")
    stmt = stmt.bindparams(slug = team_slug)
    with db() as session:
        result = session.execute(stmt)
        row = result.mappings().one()

    if row is None:
        raise LookupError(f"Could not find key value with id: {id}")

    # key = season_team_row_mapper(row)
    return row


def _get_slug_by_level_id(id: str):
    team_list = []
    stmt = text('''SELECT * FROM mhac.season_teams_with_names WHERE id = :id and archive is null''')
    stmt = stmt.bindparams(id=id)
    with db() as DB:
        result = DB.execute(stmt).mappings().all()

        for row in result:
            team_list.append(row_mapper(row))
    return team_list[0]