from fastapi import HTTPException

from sqlalchemy import Column, String
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric

from sqlalchemy.sql import text  # type: ignore
from typing import TypedDict
from uuid import uuid4, UUID

from database import db

from urllib.parse import urlparse

class WebSocketUrl(TypedDict):
    WebSocketUrl: str


def get_websocket_url():
    stmt =  '''
        SELECT * FROM mhac.websocket
    '''
    with db() as DB:
        webSocketUrl = DB.execute(stmt).fetchone()
        
    if not webSocketUrl:
        webSocketUrl = None
    return webSocketUrl

def post_websocket_url(websocket_url):
    web_address = urlparse(websocket_url)
    stmt = text('''
    Update mhac.websocket
    set websocket_url = :url, websocket_port = :port 
    ''')
    stmt = stmt.bindparams(url=f'{web_address.scheme}://{web_address.hostname}', port=web_address.port)
    with db() as DB:
        try:
            DB.execute(stmt)
            DB.commit()
        except:
            DB.rollback()
            raise HTTPException(status_code=400, detail='There was a problem saving the URL, check the format and try again.')
            
    return {"webSocketUrl": websocket_url}
    