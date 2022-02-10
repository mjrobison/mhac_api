from re import L
from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, validator
from uuid import UUID
from datetime import datetime, date, time
from dao import websockets

router = APIRouter()

class WebSocketLocation(BaseModel):
    webSocketUrl: str

class WebSocketModel(BaseModel):
    webSocketUrl: str


@router.get('/websocketUrl', tags=['obs', 'livestream'], response_model=WebSocketLocation)
def get_websocket_url() -> WebSocketLocation:
    
    results = websockets.get_websocket_url()
    if not results:
        result = {'webSocketUrl': f"wss://localhost:4444"}

    return {'webSocketUrl': f"{results['websocket_url']}:{results['websocket_port']}"}

@router.post('/websocketUrl',  status_code=201, tags=['obs', 'livestream'])
def post_websocket_url(websocket_url: WebSocketModel):
    websockets.post_websocket_url(websocket_url.webSocketUrl)

    return {"webSocketUrl": websocket_url.webSocketUrl}
