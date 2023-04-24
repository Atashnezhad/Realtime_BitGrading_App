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
    ],
)
def test_return_app_setting_event_missing_item(api, task, expected_output):
    with pytest.raises(ValueError) as e:
        event = {
            "start_ts": 1677112070,
            "end_ts": 1677112070 + 60,
            # "asset_id": 123456789,
            "task": "get_app_setting",
        }

        bg_app = BGApp(api, event)
        bg_app.run()

        assert str(e.value) == expected_output
