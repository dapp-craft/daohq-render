from threading import Thread

import uvicorn

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import main_controller

import bot

app = FastAPI()

app.mount('/static', StaticFiles(directory='static'), name='static')

app.include_router(main_controller.router, tags=['common'])


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

def start_continuous_task():
    thread = Thread(target=bot.run)
    thread.daemon = True
    thread.start()

if __name__ == '__main__':
    start_continuous_task()
    config = uvicorn.Config('server:app', port=8010, log_level='info')
    server = uvicorn.Server(config)
    server.run()
