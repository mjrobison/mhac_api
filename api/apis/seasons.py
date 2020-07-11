# import logging
# from dao import teams

# log = logging.getLogger(__name__)

# ns = Namespace('Team API - Key Version 1', description='Team API - Key Version 1')

from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date

# from dao import teams
# from apis.key_value_v1 import KeyValueOut, billing_mode_normal
# from apis import api_util #can probably remove later

# router = APIRouter()

# @router.get('/teams/', summary="Get All Teams")
# def get():
#     teams.get_list()
