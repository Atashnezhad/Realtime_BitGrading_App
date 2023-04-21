import json
import os
import unittest
from itertools import groupby
from pathlib import Path

import boto3
import pytest
import tqdm

from lambda_function import lambda_handler
from src.osu_api import Api
from src.p03_1_app import BGApp


class TestTasks(unittest.TestCase):
    def setUp(self) -> None:
        self.resources_path = Path(__file__).parent / ".." / "resources"
        self.api = Api(resources_path=self.resources_path)

    def return_cache(self):
        start_ts = 1677112070
        end_ts = 1677115068  # this the final wits timestamp

        body = {
            "start_ts": start_ts,
            "end_ts": end_ts,
            "asset_id": end_ts,
            "task": "return_cache",
        }
        event = {"body": body}
        # before running lets reset cache and make sure that the data is available in the cache
        self.reset_cache()
        lambda_handler(event, context=None)

    def reset_cache(self):
        bucket_name = "bgapptestdemo"
        file_name = "cache.json"
        s3 = boto3.resource(
            service_name="s3",
            region_name="us-east-2",
            aws_access_key_id=os.getenv("S3_AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("S3_AWS_SECRET_ACCESS_KEY"),
        )

        # write a following dict into the bucket
        data = {
            "timestamp": 1677115017,
            "provider": "osu_provider",
            "drillstring_id": "ds_1",
            "data": {"bg": 0},
        }
        s3.Object(bucket_name, file_name).put(Body=json.dumps(data))

        # read the file from the bucket again and print the data
        s3_object = s3.Object(bucket_name, file_name).get()
        # the data in body is in json format
        data_response = s3_object["Body"].read().decode("utf-8")
        data_response = json.loads(data_response)
        # assert the data inserted is same as the data_response
        self.assertEqual(data, data_response)

    def delete_cache(self):
        start_ts = 1677112070
        end_ts = 1677115068  # this the final wits timestamp

        body = {
            "start_ts": start_ts,
            "end_ts": end_ts,
            "asset_id": end_ts,
            "task": "delete_cache",
        }
        event = {"body": body}

        lambda_handler(event, context=None)

    def delete_bg_collection(self):
        start_ts = 1677112070
        end_ts = 1677115068

        body = {
            "start_ts": start_ts,
            "end_ts": end_ts,
            "asset_id": 123456789,
            "task": "delete_bg_collection",
        }
        event = {"body": body}
        lambda_handler(event, context=None)

    def run_using_lambda_handler(self):
        start_ts = 1677112070
        end_ts = 1677115068  # this the final wits timestamp

        # empty the bg_data.json file in the resources/calculated_bg folder
        path = Path(__file__).parent / ".." / "resources" / "calculated_bg"
        filename = "bg_data.json"
        address = path / filename
        with open(address, "w") as f:
            json.dump([], f)

        # also empty the mongoDB bg collection data
        self.delete_bg_collection()
        # before running lets reset cache and make sure that the initial bg is zero
        self.reset_cache()

        # make batch events between start_ts and end_ts with 60 seconds interval
        # and call the rop_app.get_wits_data() method for each batch event and print the records
        for i in range(start_ts, end_ts, 60):
            _end_ts = i + 60
            # check if i + 5 is less than end_ts
            if i + 60 > end_ts:
                _end_ts = end_ts

            body = {
                "start_ts": i,
                "end_ts": _end_ts,
                "asset_id": 123456789,
                "task": "calculate_bg",
            }
            event = {"body": body}

            lambda_handler(event, context=None)

    def run_calculated_bg(self):
        """
        In this test, the app is triggered with a batch event and the app should
        calculate the bit grade for each drill string and save the records in the database.
        The final bit grade for each drillstring (bit) is asserted.
        """
        api = Api()
        start_ts = 1677112070
        end_ts = 1677115068  # this the final wits timestamp

        # empty the bg_data.json file in the resources/calculated_bg folder
        path = Path(__file__).parent / ".." / "resources" / "calculated_bg"
        filename = "bg_data.json"
        address = path / filename
        with open(address, "w") as f:
            json.dump([], f)

        # reset the cache.json file in the resources/cache folder
        data = {
            "timestamp": 1677115017,
            "provider": "osu_provider",
            "drillstring_id": "ds_1",
            "data": {"bg": 0},
        }
        path = Path(__file__).parent / ".." / "resources" / "calculated_bg"
        filename = "cache.json"
        address = path / filename
        with open(address, "w") as f:
            json.dump(data, f)

        # also empty the mongoDB bg collection data
        self.delete_bg_collection()

        # before running lets reset cache and make sure that the initial bg is zero
        self.reset_cache()

        # make batch events between start_ts and end_ts with 60 seconds interval
        # and call the rop_app.get_wits_data() method for each batch event and print the records
        for i in range(start_ts, end_ts, 60):
            _end_ts = i + 60
            # check if i + 5 is less than end_ts
            if i + 60 > end_ts:
                _end_ts = end_ts
            event = {
                "start_ts": i,
                "end_ts": _end_ts,
                "asset_id": 123456789,
                "task": "calculate_bg",
            }
            bg_app = BGApp(api, event)
            bg_app.run()

    def test_api(self):
        query = {
            "sort": -1,
            "limit": 3,
            "fields": ["timestamp", "provider", "drill_string_id", "data"],
        }
        records = self.api.get_data(
            provider_name="osu_provider",
            data_name="wits",
            query=query,
            asset_id=123456789,
            read_from_mongo="False",
        )

        # assert the length of the records is 3
        self.assertEqual(len(records), 3)
        # assert the timestamp is sorted in descending order
        self.assertTrue(
            all(
                records[i]["timestamp"] >= records[i + 1]["timestamp"]
                for i in range(len(records) - 1)
            )
        )
        # assert the fields are present in the records
        self.assertTrue(
            all(all(field in record for field in query["fields"]) for record in records)
        )

    def test_not_defined_task_cache(self):
        start_ts = 1677112070
        end_ts = 1677115068  # this the final wits timestamp

        body = {
            "start_ts": start_ts,
            "end_ts": end_ts,
            "asset_id": 123456789,
            # "task": "delete_cache"
        }
        event = {"body": body}
        try:
            lambda_handler(event, context=None)
        except ValueError as e:
            # asset if the value error is raised
            self.assertEqual(str(e), "Invalid task: None")

    def test_events_without_needed_fields(self):
        start_ts = 1677112070
        # end_ts = 1677115068

        event = {
            "start_ts": start_ts,
            # "end_ts": end_ts,
            # "asset_id": 123456789,
            "task": "calculate_bg",
        }

        try:
            lambda_handler(event, context=None)
        except ValueError as e:
            # assert if the value error is raised
            self.assertEqual(
                str(e),
                "Missing items in the event: ['start_ts', 'end_ts', 'asset_id', 'task']",
            )

    def test_return_app_setting(self) -> None:
        start_ts = 1677112070
        end_ts = 1677115068

        event = {
            "start_ts": start_ts,
            "end_ts": end_ts,
            "asset_id": end_ts,
            "task": "get_app_setting",
        }

        app_setting = lambda_handler(event, context=None)
        app_setting_data = {
            "asset_id": 123456789,
            "data": {
                "bit_wear_constant": 30_000_000_000_000,
            },
        }
        self.assertEqual(app_setting, app_setting_data)

    def test_edit_app_setting(self) -> None:
        start_ts = 1677112070
        end_ts = 1677115068
        # write a new app setting
        event = {
            "start_ts": start_ts,
            "end_ts": end_ts,
            "asset_id": 123456789,
            "task": "edit_app_setting",
            "new_setting": {
                "data": {"bit_wear_constant": 30_000_000_000_000},
            },
        }

        lambda_handler(event, context=None)

        # now get the app setting and assert the new value
        event = {
            "start_ts": start_ts,
            "end_ts": end_ts,
            "asset_id": end_ts,
            "task": "get_app_setting",
        }

        new_app_setting = lambda_handler(event, context=None)
        assert new_app_setting["data"]["bit_wear_constant"] == 30_000_000_000_000
