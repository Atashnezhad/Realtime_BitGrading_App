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
        ('delete_cache', 'Missing items in the event: asset_id'),
        ('delete_bg_collection', 'Missing items in the event: asset_id'),
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


def return_cache(*args, **kwargs):
    print("return_cache")
    return 123


def test_get_cache(api, mocker):

    # mocker_boto3 = mocker.patch("src.p03_1_app.boto3.resource",
    #                             side_effect=return_cache)

    s3 = mocker.patch("src.p03_1_app.boto3.resource")
    s3_object = s3.Object.return_value.get.return_value
    s3_object.read.return_value.decode.return_value = '{"a": 1, "b": 2}'

    mocker.patch("json.loads", return_value=str({"a": 1, "b": 2}))

    event = {
        "start_ts": 1677112070,
        "end_ts": 1677112070 + 60,
        "asset_id": 123456789,
        "task": "return_cache",
    }

    bg_app = BGApp(api, event)
    returned_cache = bg_app.run()

    assert returned_cache == str({"a": 1, "b": 2})
