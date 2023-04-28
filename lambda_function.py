import logging
from typing import Dict
import json
from src.osu_api import Api
from src.p03_1_app import BGApp

# Initialize the logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict, context=None):
    event = json.loads(event["Body"])
    logger.info(f"Lambda function executed successfully with event {event}")
    api = Api()
    obj = BGApp(api, event)
    returned_value = obj.run()
    logger.info(f"returned_value {returned_value}")
    return returned_value
