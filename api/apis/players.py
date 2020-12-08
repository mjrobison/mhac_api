from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date

from dao import persons, players
from .teams import TeamBase
from .persons import PersonBase

router = APIRouter()
