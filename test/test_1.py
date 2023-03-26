import json
import time
import unittest
from itertools import groupby
from pathlib import Path

from lambda_function import lambda_handler
from src.osu_api import Api
from src.p03_1_app import BGApp


class Test1(unittest.TestCase):
    def setUp(self) -> None:
        self.resources_path = Path(__file__).parent / ".." / "resources"
        self.api = Api(resources_path=self.resources_path)

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

    def test_bg_app_get_wits_data(self):
        api = Api()
        start_ts = 1677112070
        end_ts = 1677112083
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
            # print(event)
            bg_app = BGApp(api, event)
            records = bg_app.get_wits_data()
            print(records)
            # sleep for 5 second
            time.sleep(1)

    @unittest.skip
    def test_calculated_bg(self):
        """
        In this test, the app is triggered with a batch event and the app should
        calculate the bit grade for each drill string and save the records in the database.
        The final bit grade for each drillsting (bit) is asserted.
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

        # read the bg_data.json file and assert the bit grade for each drill string
        with open(address, "r") as f:
            records = json.load(f)
        # group the records by drill string id
        records = {
            k: list(v) for k, v in groupby(records, key=lambda x: x["drillstring_id"])
        }
        # get the last record for each drill string in list
        records = [v[-1] for k, v in records.items()]
        expected_calculated_bg = [
            0.912,
            2.531,
            1.064,
        ]  # note if the data is re-generated using p01_2 file then these values should be edited
        # based on new values.
        for case, expected_bg in zip(records, expected_calculated_bg):
            assert case.get("data").get("bg") == expected_bg

    # skip this test for now
    # @unittest.skip
    def test_lambda_handler(self):
        api = Api()
        start_ts = 1677112070
        end_ts = 1677115068  # this the final wits timestamp

        # empty the bg_data.json file in the resources/calculated_bg folder
        path = Path(__file__).parent / ".." / "resources" / "calculated_bg"
        filename = "bg_data.json"
        address = path / filename
        with open(address, "w") as f:
            json.dump([], f)

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

            lambda_handler(api, event, context=None)

    def test_return_cache(self):
        api = Api()
        start_ts = 1677112070
        end_ts = 1677115068  # this the final wits timestamp

        body = {
            "start_ts": start_ts,
            "end_ts": end_ts,
            "asset_id": end_ts,
            "task": "return_cache",
        }
        event = {"body": body}

        lambda_handler(api, event, context=None)

    # skip this test for now
    @unittest.skip
    def test_delete_cache(self):
        api = Api()
        start_ts = 1677112070
        end_ts = 1677115068  # this the final wits timestamp

        body = {
            "start_ts": start_ts,
            "end_ts": end_ts,
            "asset_id": end_ts,
            "task": "delete_cache",
        }
        event = {"body": body}

        lambda_handler(api, event, context=None)

    def test_not_defined_task_cache(self):
        api = Api()
        start_ts = 1677112070
        end_ts = 1677115068  # this the final wits timestamp

        body = {
            "start_ts": start_ts,
            "end_ts": end_ts,
            "asset_id": end_ts,
            # "task": "delete_cache"
        }
        event = {"body": body}
        try:
            lambda_handler(api, event, context=None)
        except ValueError as e:
            # asset if the value error is raised
            self.assertEqual(str(e), "Invalid task: None")

    def test_events_without_needed_fields(self):
        api = Api()
        start_ts = 1677112070
        # end_ts = 1677115068

        body = {
            "start_ts": start_ts,
            # "end_ts": end_ts,
            # "asset_id": end_ts,
            "task": "calculate_bg",
        }
        event = {"body": body}

        try:
            lambda_handler(api, event, context=None)
        except ValueError as e:
            # asset if the value error is raised
            self.assertEqual(
                str(e),
                "Missing items in the event: ['start_ts', 'end_ts', 'asset_id', 'task']",
            )
