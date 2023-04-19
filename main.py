import json

import pydantic
from fastapi import FastAPI
from typing import Dict, Any, Optional
from src.osu_api import Api
from src.p03_1_app import BGApp

app = FastAPI()


@app.get("/")
def home():
    return {"health_check": "OK"}


@app.get("/task/{event}")
def task(event: str):
    api = Api()
    event_dict = json.loads(event)
    # print(event_dict)
    obj = BGApp(api, event_dict)
    returned_value = obj.run()
    return returned_value
