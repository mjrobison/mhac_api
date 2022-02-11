import time, os
from fastapi import FastAPI, Request, APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
# from database import Base
# from dao import models, teams
import json

import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from config import config, LogConfig
from apis import api_router

import logging
from logging.config import dictConfig

dictConfig(LogConfig().dict())
logger = logging.getLogger("mhac_api")

app = FastAPI(title='MHAC API', version='1.0', description='MHAC API - v1')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_settings():
    env = os.environ.get('API_ENV', 'development')
    return config.get(env)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    # response.headers["Access-Control-Allow-Origin"] = "https://mhacsports.com"
    response.headers["Access-Control-Allow-Origin"] = "*"
    # response.headers["Access-Control-Allow-Origin"] = "*"
    # response.headers["Access-Control-Allow-Origin"] = "*"
    return response

app.include_router(api_router)


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            // var ws = new WebSocket(`ws://192.168.1.82:8000/ws/${client_id}`);
            var ws = new WebSocket(`ws://192.168.1.74:4444`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        print(json.dumps(message, indent=3))
        await websocket.send_text(json.dumps(message))

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


# manager = ConnectionManager()

# @app.get("/")
# async def get():
#     return HTMLResponse(html)


# @app.websocket("/ws/{client_id}")
# async def websocket_endpoint(websocket: WebSocket, client_id: int):
#     await manager.connect(websocket)
#     try:
#         while True:
#             data = await websocket.receive_text()
#             await manager.send_personal_message(f"You wrote: {data}", websocket)
#             await manager.broadcast(f"{data}")
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)
#         await manager.broadcast(f"Client #{client_id} left the chat")

# async def get_last_state(game_id):
#     return '{"game_time":"7:55", "clock_status": "running}'

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)

    # {"request-type": "BroadcastCustomMessage","realm": "1", "data": {"action": "incrementAway", "value": 10},"message-id": "1"}
    # {"request-type": "BroadcastCustomMessage","realm": "1", "data": {"action": "setAway", "value": 3},"message-id": "1"}
    # {"request-type": "BroadcastCustomMessage","realm": "1", "data": {"action": "toggle_time", "value": 0},"message-id": "1"}
    # {"request-type": "GetSceneList","message-id": "1"}

