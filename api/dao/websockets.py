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


def get_websocket_url(DB=db()):
    stmt =  '''
        SELECT * FROM mhac.websocket
    '''
    
    webSocketUrl = DB.execute(stmt).fetchone()
    print(webSocketUrl)
    DB.close()

    return webSocketUrl

def post_websocket_url(websocket_url, DB=db()):
    web_address = urlparse(websocket_url)
    stmt = text('''
    Update mhac.websocket
    set websocket_url = :url, websocket_port = :port 
    ''')
    stmt = stmt.bindparams(url=f'{web_address.scheme}://{web_address.hostname}', port=web_address.port)
    try:
        DB.execute(stmt)
        DB.commit()
        DB.close()
    except:
        DB.rollback()
        DB.close()
        raise HTTPException(status_code=400, detail='There was a problem saving the URL, check the format and try again.')
        
    return {"webSocketUrl": websocket_url}
    