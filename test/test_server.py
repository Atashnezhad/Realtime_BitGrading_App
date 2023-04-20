import json

import pytest
import requests


@pytest.fixture
def url():
    url = "http://127.0.0.1:8080"
    return url


# skip this test for now
@pytest.mark.skip
def test_server_get(url):
    # url = "http://127.0.0.1:8080"
    response = requests.get(url)
    print("\n", response.json())
    assert response.status_code == 200
    assert response.json() == {"health_check": "OK"}


@pytest.mark.skip
def test_server_task_return_cache(url):
    event_dict = {
        "start_ts": 1677112070,
        "end_ts": 1677112070 + 60,
        "asset_id": 123456789,
        "task": "return_cache",
    }
    event_str = json.dumps(event_dict)
    # print(event_str)
    url = f"http://127.0.0.1:8080/task/{event_str}"
    response = requests.get(url)
    assert response.status_code == 200
    print("\n", response.json())


@pytest.mark.skip
def test_server_task_get_app_setting(url):
    event_dict = {
        "start_ts": 1677112070,
        "end_ts": 1677112070 + 60,
        "asset_id": 123456789,
        "task": "get_app_setting",
    }
    event_str = json.dumps(event_dict)
    # print(event_str)
    url = f"http://127.0.0.1:8080/task/{event_str}"
    response = requests.get(url)
    assert response.status_code == 200
    print("\n", response.json())
