from fastapi import FastAPI
from typing import Dict
from src.osu_api import Api
from src.p03_1_app import BGApp

app = FastAPI()


@app.get("/")
def home():
    return {"health_check": "OK"}


@app.post("/predict")
def lambda_handler(api: Api, event: Dict, context=None):
    event = event["body"]
    obj = BGApp(api, event)
    returned_value = obj.run()
    return returned_value
