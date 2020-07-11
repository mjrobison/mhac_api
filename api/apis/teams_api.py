# import logging
# from dao import teams

# log = logging.getLogger(__name__)

# ns = Namespace('Team API - Key Version 1', description='Team API - Key Version 1')

from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date

from dao import teams
# from apis.key_value_v1 import KeyValueOut, billing_mode_normal
# from apis import api_util #can probably remove later

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


@router.get('/teams/', response_model=List[TeamBase], summary="Get All Teams")
def get():
    return teams.get_list()


# class PromotionGroup(TypedDict):
#     group_id: str
#     group_name: str = ''
#     start_dt: str = ''
#     end_dt: str = None
#     created_by: str = ''
#     updated_by: str = None
#     created_on: datetime.datetime
#     updated_on: datetime.datetime
#     billing_mode: Dict = {}
#     responsible_party: Dict = {}
#     billing_party: Dict = {}
#     item_source: Dict = {}