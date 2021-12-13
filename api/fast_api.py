import time, os
from fastapi import FastAPI, Request, APIRouter
# from database import Base
# from dao import models, teams

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
    response.headers["Access-Control-Allow-Origin"] = "*"
    # response.headers["Access-Control-Allow-Origin"] = "*"
    # response.headers["Access-Control-Allow-Origin"] = "*"
    # response.headers["Access-Control-Allow-Origin"] = "*"
    return response

app.include_router(api_router)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)