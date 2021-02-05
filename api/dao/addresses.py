from fastapi import Depends, HTTPException
from sqlalchemy import Column, String
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric

from sqlalchemy.sql import text # type: ignore
from typing import TypedDict, List, Dict, Any, Optional
from uuid import uuid4
from sqlalchemy.dialects.postgresql import JSON, UUID

from database import db, get_db

base_query = text('''SELECT * FROM mhac.addresses ''')

class Address(TypedDict):
    address_id = UUID
    location_name = Optional[str]
    address_line_1 = str
    address_line_2 = Optional[str]
    city = str
    state = str
    postal_code = str


def row_mapper(row) -> Address:
    Address = {
        'address_id': row['id'],
        'location_name': row['name'],
        'address_line_1': row['address_line_1'],
        'address_line_2': row['address_line_2'],
        'city': row['city'],
        'state': row['state'],
        'postal_code': row['postal_code']        
    }
    return Address

def get_address_with_id(id:UUID):
    DB = db()
    query = text(f'''{base_query} WHERE id = :id ''')

    query = query.bindparams(id = id)
    results = DB.execute(query).fetchone()
    
    if results:
        result = row_mapper(results)
        DB.close()
        return result
    
    DB.close()
    raise HTTPException(status_code=404)

    