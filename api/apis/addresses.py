from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date



class Address(BaseModel):
    address_id: UUID
    location_name: Optional[str]
    address_line_1: str
    address_line_2: Optional[str]
    city: str
    state: str
    postal_code: Optional[str]