from fastapi import Depends, HTTPException
from sqlalchemy import Column, String
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    DateTime,
    Date,
    Numeric,
)

from sqlalchemy.sql import text  # type: ignore
from typing import TypedDict, Optional
from sqlalchemy.dialects.postgresql import UUID

from database import db


class Address(TypedDict):
    address_id: UUID
    location_name: Optional[str]
    address_line_1: str
    address_line_2: Optional[str]
    city: str
    state: str
    postal_code: str
    address_id: UUID
    location_name: Optional[str]
    address_line_1: str
    address_line_2: Optional[str]
    city: str
    state: str
    postal_code: str


def row_mapper(row) -> Address:
    Address = {
        "address_id": row["id"],
        "location_name": row["name"],
        "address_line_1": row["address_line_1"],
        "address_line_2": row["address_line_2"],
        "city": row["city"],
        "state": row["state"],
        "postal_code": row["postal_code"],
    }
    return Address


def get_address_with_id(id: UUID):
    query = text(f"""{base_query} WHERE id = :id """)

    query = query.bindparams(id=id)
    with db() as DB:
        results = DB.execute(query).mappings().one()

        if len(results) < 1:
            raise HTTPException(status_code=404)

        result = row_mapper(results)

    return result


def create():
    stmt = text(
        """INSERT INTO mhac.addresses()
                VALUES ()
                RETURNING ID"""
    )

    with db() as DB:
        result = DB.execute(stmt).mappings().one()

    return result
