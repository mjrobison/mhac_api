from sqlalchemy.sql import text  # type: ignore
from typing import TypedDict, List, Dict, Any, Optional
from uuid import uuid4, UUID

from database import db

from .teams import get_with_uuid as get_team, SeasonTeam, get_with_slug
from .levels import get_level_by_id

from .seasons import get_by_year_and_level


class Height(TypedDict):
    feet: Optional[int]
    inches: Optional[int]


class Person(TypedDict):
    first_name: str
    last_name: str
    person_type: int
    team: UUID
    team_id: UUID
    age: Optional[int]
    height: Optional[Height]
    number: int
    position: Optional[str]


class PlayerCreate(TypedDict):
    first_name: str
    last_name: str
    person_type: int
    team: UUID
    season_roster: List[SeasonTeam]
    age: Optional[int]
    height: Optional[Height]
    player_number: Optional[int]
    position: Optional[str]


class PlayerReturn(Person):
    id: UUID
    season_roster: Optional[List[str]]
    age: int


def calc_age(birth_date):
    from dateutil.relativedelta import relativedelta
    from datetime import date

    return relativedelta(date.today(), birth_date).years


def break_height(inches):
    # print(inches)
    if inches:
        feet = int(int(inches) / 12)
        inches = int(int(inches) % 12)
        return feet, inches
    return 0, 0


def combine_height(height: Height):
    return (height.feet * 12) + height.inches


def player_row_mapper(row) -> PlayerReturn:
    feet, inches = break_height(row["height"] if row["height"] is not None else 0)
    PlayerReturn = {
        "id": row["id"],
        "first_name": row["first_name"],
        "last_name": row["last_name"],
        # 'age': calc_age(row['birth_date']),
        # 'birth_date': row['birth_date'],
        "age": row["age"],
        "height": {"feet": feet, "inches": inches},
        # TODO: Provide a lookup,
        "person_type": row["person_type"],
        "team": row["team_id"],
        "team_id": row["team_id"],
        "player_number": row["number"],
        "position": row["position"],
        "season_roster": [get_team(i) for i in row["season_roster"].split(",")],
    }
    return PlayerReturn


def get(id) -> Person:
    stmt = text("""SELECT person.* FROM mhac.person WHERE id = :id """)
    stmt = stmt.bindparams(id=id)

    with db() as session:
        result = session.execute(stmt)
        row = result.fetchone()

    if row is None:
        raise LookupError(f"Could not find key value with id: {id}")

    return row


def get_list(person_type) -> List[Person]:
    player_list = []
    stmt = text(
        """SELECT person.* FROM mhac.person INNER JOIN mhac.person_type ON person.person_type = person_type.id WHERE person_type.type = :person_type """
    )
    with db() as session:
        result = session.execute(stmt.bindparams(person_type=person_type))
        for row in result:
            player_list.append(player_row_mapper(row))
    if len(player_list) == 0:
        raise LookupError("No persons with that type were found")
    return player_list


def get_team_list(slug, season_level: Optional[str] = None):
    player_list = []

    base_query = text(
        """ 
        SELECT 
        person.id
        , person.first_name
        , person.last_name
        , person.age
        , person.height
        , person.person_type
        , person.team_id
        , person.position
        , team_rosters.jersey_number as number
        , string_agg(season_team_id::text, ',') AS season_roster
        , string_agg(level_id::text,',') 
        FROM mhac.team_rosters
        INNER JOIN mhac.season_teams_with_names as teams
            ON team_rosters.season_team_id = teams.id 
        INNER JOIN mhac.person
            ON team_rosters.player_id = person.id
        INNER JOIN mhac.seasons
            ON seasons.id = teams.season_id
        WHERE teams.archive is null
        and teams.slug = :slug"""
    )
    group_by = text(
        """GROUP BY person.id, person.first_name, person.last_name, person.age, person.height, person.person_type, person.team_id, person.position, team_rosters.jersey_number"""
    )

    stmt = text(f"{base_query} {group_by}")
    stmt = stmt.bindparams(slug=slug)

    if season_level:
        stmt = text(
            f"{base_query} and team_rosters.season_team_id = :season_level {group_by}"
        )
        stmt = stmt.bindparams(slug=slug, season_level=season_level)

    with db() as session:
        try:
            result = session.execute(stmt)
            for row in result:
                player_list.append(player_row_mapper(row))
        except Exception as exc:
            print(str(exc))
            raise
    if len(player_list) == 0:
        raise LookupError(f"No players found for {slug}")

    return player_list


def update(id, Player: PlayerCreate):
    # TODO: Compare incoming with existing and update the new field
    # TODO: Remove a seasonTeam

    # Check Season Teams
    query = text(
        """ 
    SELECT * FROM mhac.team_rosters
    INNER JOIN mhac.season_teams_with_names
        ON team_rosters.season_team_id = season_teams_with_names.id
    WHERE player_id = :player_id
        AND season_teams_with_names.archive is null
    """
    )
    query = query.bindparams(player_id=Player.id)
    with db() as session:
        results = session.execute(query).fetchall()

        if len(results) > len(Player.season_roster):
            for r in results:
                if r not in Player.season_roster:
                    update = text(
                        """DELETE FROM mhac.team_rosters WHERE roster_id = :roster_id """
                    )
                    update = update.bindparams(roster_id=r.roster_id)
                    session.execute(update)

        for season_team in Player.season_roster:
            stmt = text(
                """INSERT INTO mhac.team_rosters(season_team_id, player_id, jersey_number)
            VALUES
            (:season_team_id, :player_id, :number) 
            ON CONFLICT ON CONSTRAINT ux_season_team_player_id 
            DO UPDATE
            SET jersey_number = :number"""
            )

            stmt = stmt.bindparams(
                season_team_id=season_team.team_id,
                player_id=id,
                number=Player.player_number,
            )
            session.execute(stmt)
        player_height = combine_height(Player.height)
        stmt = text(
            """UPDATE mhac.person 
        SET first_name = :first_name, last_name = :last_name, age = :age, position = :position, height = :height, number = :player_number, person_type = :person_type
        WHERE id = :id"""
        )
        stmt = stmt.bindparams(
            first_name=Player.first_name,
            last_name=Player.last_name,
            age=Player.age,
            position=Player.position,
            height=player_height,
            player_number=Player.player_number,
            id=Player.id,
            person_type="1",
        )

        try:
            session.execute(stmt)
            session.commit()
        except Exception as exc:
            print(str(exc))


# def create_player(player):
#     try:
#         player_height = combine_height(player.height)
#         if player_height == 0:
#             player_height = None

#         player_id = uuid4()
#         stmt = text(
#             """INSERT INTO mhac.person (id, first_name, last_name, age, height, number, position, person_type, team_id)
#         VALUES (:id, :first_name, :last_name, :age, :height, :number, :position, :person_type, :team_id)
#         ON CONFLICT ON CONSTRAINT ux_persons
#         DO
#         UPDATE
#         SET first_name = :first_name, last_name = :last_name, age = :age, height=:height, number = :number, position=:position
#         RETURNING id"""
#         )
#         stmt = stmt.bindparams(
#             id=player_id,
#             first_name=player.first_name,
#             last_name=player.last_name,
#             age=player.age,
#             height=player_height,
#             number=player.player_number,
#             position=player.position,
#             person_type="1",
#             team_id=team_id[0]['team_id'],
#         )
#         with db() as session:
#             result = session.execute(stmt).fetchone()
#             if result:
#                 player_id = result[0]

#             stmt = """SELECT * FROM mhac.season_teams_with_names 
#             WHERE team_id = :team_id 
#                 AND lower(level_name) = :level_name 
#                 AND season_id = :season_id;
#             """
#             stmt = stmt.bindparams(team_id = team_id[0]['team_id'], level_name=player.level_name.lower(), season_id= season_id['season_id'])
#             season_roster = session.execute(stmt).mappings().all()
            
#             for season_team in season_roster:
#                 stmt = text(
#                     """INSERT INTO mhac.team_rosters(season_team_id, player_id, jersey_number)
#                     VALUES
#                     (:season_team_id, :player_id, :number)
#                     ON CONFLICT ON CONSTRAINT ux_season_team_player_id
#                     DO UPDATE
#                     SET jersey_number = :number"""
#                 )
#                 stmt = stmt.bindparams(
#                     season_team_id=season_team.team_id,
#                     player_id=player_id,
#                     number=player.player_number,
#                 )

#                 session.execute(stmt)

#             session.commit()
#             message = "Successfully added player"
#             # TODO: Add to a "roster"
#     except Exception as exc:
#         message = str(exc)
#         print(message)
#         return {500: message}


def import_player(player):
    season_id = get_by_year_and_level(player.year, player.level_name)
    season_id['season_id']
    team_id = get_with_slug(player.team_slug)
    print(team_id)
    message = ""

    try:
        player_height = combine_height(player.height)
        if player_height == 0:
            player_height = None

        player_id = uuid4()
        stmt = text(
            """INSERT INTO mhac.person (id, first_name, last_name, age, height, number, position, person_type, team_id)
        VALUES (:id, :first_name, :last_name, :age, :height, :number, :position, :person_type, :team_id)
        ON CONFLICT ON CONSTRAINT ux_persons
        DO
        UPDATE
        SET first_name = :first_name, last_name = :last_name, age = :age, height=:height, number = :number, position=:position
        RETURNING id"""
        )
        stmt = stmt.bindparams(
            id=player_id,
            first_name=player.first_name,
            last_name=player.last_name,
            age=player.age,
            height=player_height,
            number=player.player_number,
            position=player.position,
            person_type="1",
            team_id=team_id['team_id'],
        )
        with db() as session:
            result = session.execute(stmt).fetchone()
            if result:
                player_id = result[0]

            stmt = text("""SELECT * FROM mhac.season_teams_with_names 
            WHERE team_id = :team_id 
                AND lower(level_name) = :level_name 
                AND season_id = :season_id;
            """)
            stmt = stmt.bindparams(team_id = team_id['team_id'], level_name=player.level_name.lower(), season_id= season_id['season_id'])
            season_roster = session.execute(stmt).mappings().all()
            
            for season_team in season_roster:
                print(season_team)
                stmt = text(
                    """INSERT INTO mhac.team_rosters(season_team_id, player_id, jersey_number)
                    VALUES
                    (:season_team_id, :player_id, :number)
                    ON CONFLICT ON CONSTRAINT ux_season_team_player_id
                    DO UPDATE
                    SET jersey_number = :number"""
                )
                print(stmt)
                stmt = stmt.bindparams(
                    season_team_id=season_team['id'],
                    player_id=player_id,
                    number=player.player_number,
                )
                

                session.execute(stmt)

            session.commit()
            message = "Successfully added player"
            # TODO: Add to a "roster"
    except Exception as exc:
        message = str(exc)
        print(message)
        return {500: message}


def get_still_active_players():
    # TODO: Get a list of player still active include last team played for
    # TODO: Write and endpoint to update this years rosters with current team
    ...
