from typing import Dict
import json
from src.p03_1_app import BGApp
from src.osu_api import Api
import logging

# Initialize the logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict, context=None):
    # Print a message to the logs
    logger.info(f"Lambda function executed successfully with event {event}")

    if isinstance(event, str):
        event = json.loads(event)

    if "body" in event:
        event = json.loads(event["body"])

    logger.info(f"Lambda function executed successfully with event {event}")
    api = Api()
    obj = BGApp(api, event)
    returned_value = obj.run()
    logger.info(f"returned_value {returned_value}")
    return returned_value

