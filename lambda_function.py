from typing import Dict

from src.p03_1_app import BGApp
from src.osu_api import Api


def lambda_handler(api: Api, event: Dict, context=None):
    event = event["body"]
    obj = BGApp(api, event)
    returned_value = obj.run()
    return returned_value

