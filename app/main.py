import json

from fastapi import FastAPI
from pydantic import BaseModel
from src.osu_api import Api
from src.p03_1_app import BGApp

app = FastAPI()


# Define the Pydantic model for the task payload
class Event(BaseModel):
    start_ts: int = 1677112070
    end_ts: int = 1677115068
    asset_id: int = 123456789
    task: str = "return_cache"


@app.get("/")
def home():
    return {"health_check": "OK"}


@app.post("/task")
def task(event: Event):
    api = Api()
    event_dict = event.dict()
    # print(event_dict)
    obj = BGApp(api, event_dict)
    returned_value = obj.run()
    return returned_value

# here is an example of event in the api
# {"start_ts": 1677112070,"end_ts": 1677115068,    "asset_id": 123456789,    "task": "return_cache"}
