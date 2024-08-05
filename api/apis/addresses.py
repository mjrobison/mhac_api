from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date
from dao.addresses import get_address_with_id

router = APIRouter()

class Address(BaseModel):
    address_id: UUID
    location_name: Optional[str]
    address_line_1: str
    address_line_2: Optional[str]
    city: str
    state: str
    postal_code: Optional[str]


@router.get('/address/{address_id}', response_model=Address, tags=['address', 'teams'])
def address(address_id: UUID):
   return get_address_with_id(address_id)