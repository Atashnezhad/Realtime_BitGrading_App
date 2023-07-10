import json
from pydantic import BaseModel
from fastapi import FastAPI

from src.osu_api import Api
from src.p03_1_app import BGApp

app = FastAPI()


# Define the Pydantic model for the task payload
class Event(BaseModel):
    start_ts: int
    end_ts: int
    asset_id: int
    task: str


@app.get("/")
def home():
    return {"health_check": "OK"}


@app.post("/task/{event}")
def task(event: str):
    api = Api()
    event_dict = json.loads(event)
    # print(event_dict)
    obj = BGApp(api, event_dict)
    returned_value = obj.run()
    return returned_value

# here is an example of event in the api
# {"start_ts": 1677112070,"end_ts": 1677115068,    "asset_id": 123456789,    "task": "return_cache"}