import json
import unittest
from itertools import groupby
from pathlib import Path
from typing import List, Dict
from unittest.mock import patch
from unittest import mock

import boto3
import tqdm

import src.p03_1_app
from lambda_function import lambda_handler
from src.osu_api import Api
from src.p03_1_app import BGApp


class TestApp(unittest.TestCase):
    def setUp(self) -> None:
        self.resources_path = Path(__file__).parent / ".." / "resources"
        self.api = Api(resources_path=self.resources_path)

    def get_data(self, *args, **kwargs) -> List[Dict]:
        if kwargs.get("data_name") == "wits":
            # read the wits data from the resources folder
            with open(self.resources_path / "wits.json") as f:
                wits_data = json.load(f)

            # separate the wits data based on the start and end timestamp specified in the query
            start_ts = kwargs.get("query").get("ts_min")
            end_ts = kwargs.get("query").get("ts_max")
            # filter the wits data based on the start and end timestamp
            wits_data = list(
                filter(lambda x: start_ts <= x["timestamp"] < end_ts, wits_data)
            )

            return wits_data

        if kwargs.get("data_name") == "ds_data":
            # read the ds data from the resources folder
            with open(self.resources_path / "ds_data.json") as f:
                ds_data = json.load(f)

            return ds_data

        if kwargs.get("data_name") == "dhm_data":
            # read the dhm data from the resources folder
            with open(self.resources_path / "dhm_data.json") as f:
                dhm_data = json.load(f)
            return dhm_data

    def post_bg(self, *args, **kwargs) -> None:
        print("post_bg called")
        data = args[0]
        # get the bg out of the data
        bgs = [record["data"]["bg"] for record in data]
        print(bgs)
        return None

    def get_cache(self, *args, **kwargs) -> Dict:
        print("get_cache called")

    @mock.patch.object(src.p03_1_app.BGApp, "get_cache")
    @mock.patch.object(src.p03_1_app.BGApp, "post_bg")
    @mock.patch.object(Api, "get_data")
    def test_bg_app(
        self,
        mock_api_get_data_method,
        mock_bgapp_post_method,
        mock_bgapp_get_cache_method,
    ):
        mock_api_get_data_method.side_effect = self.get_data
        mock_bgapp_post_method.side_effect = self.post_bg
        mock_bgapp_get_cache_method.side_effect = self.get_cache

        start_ts = 1677112070
        end_ts = 1677115068  # this the final wits timestamp

        # make batch events between start_ts and end_ts with 60 seconds interval
        # and call the rop_app.get_wits_data() method for each batch event and print the records
        # with patch.object(Api, "get_data", side_effect =self.get_data) as mock_method:
        for i in tqdm.tqdm(range(start_ts, end_ts, 60)):
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
            bg_app = BGApp(self.api, event)
            bg_app.run()
            assert mock_api_get_data_method.called
            assert mock_bgapp_post_method.called

    # here we patch using context manager
    # def test_bg_app_2(self):
    #
    #     start_ts = 1677112070
    #     end_ts = 1677115068  # this the final wits timestamp
    #
    #     # make batch events between start_ts and end_ts with 60 seconds interval
    #     # and call the rop_app.get_wits_data() method for each batch event and print the records
    #     with patch.object(Api, "get_data", side_effect =self.get_data) as mock_method:
    #         for i in tqdm.tqdm(range(start_ts, end_ts, 60)):
    #             _end_ts = i + 60
    #             # check if i + 5 is less than end_ts
    #             if i + 60 > end_ts:
    #                 _end_ts = end_ts
    #             event = {
    #                 "start_ts": i,
    #                 "end_ts": _end_ts,
    #                 "asset_id": 123456789,
    #                 "task": "calculate_bg",
    #             }
    #             # print(event)
    #             bg_app = BGApp(self.api, event)
    #             bg_app.run()
    #             assert mock_method.called
