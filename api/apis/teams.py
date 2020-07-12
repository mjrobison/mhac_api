from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date

from dao import teams


router = APIRouter()

class TeamBase(BaseModel):
    team_id: UUID
    team_name: str
    team_mascot: str
    main_color: str 
    secondary_color: str
    website: Optional[str] 
    logo_color: str
    logo_grey: str 
    slug: str 


@router.get('/getTeams', response_model=List[TeamBase], summary="Get All Teams")
async def get():
    return teams.get_list()

@router.get('/getTeams/<slug>', response_model=TeamBase, summary="Get an invididual team")
async def getTeam(slug):
    return teams.get(slug)
