import json
from typing import Dict

from src.p03_1_app import BGApp
from src.osu_api import Api


def lambda_handler(api: Api, event: Dict, context):
    event = json.loads(event["body"])
    bg_app = BGApp(api, event)
    bg_app.run()
    print('Hello from Lambda')
    return 'Hello from Lambda'
