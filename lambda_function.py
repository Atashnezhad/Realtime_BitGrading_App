from typing import Dict

from src.p03_1_app import BGApp
from src.osu_api import Api


def lambda_handler(api: Api, event: Dict, context):
    event = event["body"]
    bg_app = BGApp(api, event)
    output = bg_app.run(_return=True)
    print(output)
