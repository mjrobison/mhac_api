# from sqlalchemy import Column, String
# from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric

from sqlalchemy.sql import text  # type: ignore
from typing import TypedDict, List, Dict, Any, Optional
from uuid import uuid4, UUID

# from sqlalchemy.dialects.postgresql import JSON, UUID
from datetime import date, timedelta, datetime
from database import db

base_query = text("""SELECT * FROM mhac.levels""")


class LevelBase(TypedDict):
    level_name: str


class Level(LevelBase):
    id: int


class LevelOut(TypedDict):
    id: int
    level_name: str


def row_mapper(row) -> Level:
    Level = {"id": row["id"], "level_name": row["level_name"]}
    return Level


def get_level_by_id(id) -> Level:
    stmt = text(f"""{base_query} WHERE id = :id""")
    stmt = stmt.bindparams(id=id)
    with db() as DB:
        results = DB.execute(stmt).mappings().one()
    return results


def get_by_name(level_name) -> Level:
    stmt = text(f"""{base_query} WHERE level_name = :level_name""")
    stmt = stmt.bindparams(level_name=level_name)
    with db() as DB:
        results = DB.execute(stmt)
    return results.fetchone()


def get_list() -> List[Level]:
    stmt = text(f"""{base_query}""")
    with db() as DB:
        results = DB.execute(stmt).mappings().all()

    level_list = []
    for result in results:
        level_list.append(row_mapper(result))
    return level_list


def create(level: LevelBase):
    stmt = text(
        """INSERT INTO mhac.levels(level_name) 
                    VALUES
                    (:level_name)"""
    )
    stmt = stmt.bindparams(level_name=level.level_name)
    with db() as DB:
        DB.execute(stmt)
        DB.commit()
    return {200: "Success"}


def update(level: Level):
    stmt = text(
        """UPDATE mhac.levels
                    SET level_name =:level_name
                    WHERE id = :id """
    )
    stmt = stmt.bindparams(id=level.id, level_name=level.level_name)
    with db() as DB:
        DB.execute(stmt)
        DB.commit()
    return {200: "Success"}
