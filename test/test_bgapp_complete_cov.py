import json

import boto3
import pytest
from src.osu_api import Api
from src.p03_1_app import BGApp


@pytest.fixture
def api():
    return Api()


@pytest.mark.parametrize(
    "task, expected_output",
    [
        ("get_app_setting", "Missing items in the event: asset_id"),
        ("edit_app_setting", "Missing items in the event: asset_id"),
        ("return_cache", "Missing items in the event: asset_id"),
        ("delete_cache", "Missing items in the event: asset_id"),
        ("delete_bg_collection", "Missing items in the event: asset_id"),
    ],
)
def test_return_app_setting_event_missing_item(api, task, expected_output):
    with pytest.raises(ValueError) as e:
        event = {
            "start_ts": 1677112070,
            "end_ts": 1677112070 + 60,
            # "asset_id": 123456789,
            "task": task,
        }

        bg_app = BGApp(api, event)
        bg_app.run()

        assert str(e.value) == expected_output


class DecodeObject:
    def __init__(self, *args):
        self._body = json.dumps(
            {
                "timestamp": 1677115067,
                "provider": "osu_provider",
                "drillstring_id": "ds_3",
                "data": {"bg": 0.712},
            }
        )

    def decode(self, *args):
        return self._body

    @staticmethod
    def expected_json():
        return {
            "timestamp": 1677115067,
            "provider": "osu_provider",
            "drillstring_id": "ds_3",
            "data": {"bg": 0.712},
        }


class BodyObject:
    def read(self):
        return DecodeObject()


class CustomObject:
    def __getitem__(self, key):
        if key == "Body":
            return BodyObject()
        else:
            raise KeyError(f"Invalid key: {key}")


def test_get_cache(api, mocker):
    boto3_resource = mocker.patch("src.p03_1_app.boto3.resource")
    boto3_resource.return_value.Object.return_value.get.return_value = CustomObject()

    event = {
        "start_ts": 1677112070,
        "end_ts": 1677112070 + 60,
        "asset_id": 123456789,
        "task": "return_cache",
    }

    bg_app = BGApp(api, event)
    returned_cache = bg_app.run()

    assert returned_cache == DecodeObject.expected_json()


# another way is to just mock the get_cache method from the BGApp class
def test_get_cache_2(api, mocker):
    mocker.patch(
        "src.p03_1_app.BGApp.get_cache", return_value=DecodeObject.expected_json()
    )

    event = {
        "start_ts": 1677112070,
        "end_ts": 1677112070 + 60,
        "asset_id": 123456789,
        "task": "return_cache",
    }

    bg_app = BGApp(api, event)
    returned_cache = bg_app.run()

    assert returned_cache == DecodeObject.expected_json()


def return_cache(*args):
    return {
        "timestamp": 1677115067,
        "provider": "osu_provider",
        "drillstring_id": "ds_3",
        "data": {"bg": 0.712},
    }


# or just mock the json.loads method
def test_get_cache_3(api, mocker):
    mocker.patch("src.p03_1_app.boto3", return_value=None)
    # patch the json and call the return_cache function
    mocker.patch("json.loads", side_effect=return_cache)
    event = {
        "start_ts": 1677112070,
        "end_ts": 1677112070 + 60,
        "asset_id": 123456789,
        "task": "return_cache",
    }

    bg_app = BGApp(api, event)
    returned_cache = bg_app.run()
    assert returned_cache == return_cache()
