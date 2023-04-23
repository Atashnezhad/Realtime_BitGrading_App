import json

import pytest
from pathlib import Path

from src.osu_api import Api


@pytest.fixture
def api():
    return Api()


@pytest.fixture
def query():
    query = {
        "sort": -1,
        "limit": 3,
        "fields": ["timestamp", "provider", "drill_string_id", "data"],
    }
    return query


def test_raise_value_error_provider_name(api, query):
    with pytest.raises(ValueError) as e:
        api.get_data(
            provider_name="",
            data_name="wits",
            query=query,
            asset_id=123456789,
            read_from_mongo="False",
        )

    assert str(e.value) == "Provider is not provided."


def test_raise_value_error_data_name(api, query):
    with pytest.raises(ValueError) as e:
        api.get_data(
            provider_name="osu_provider",
            data_name="",
            query=query,
            asset_id=123456789,
            read_from_mongo="False",
        )

    assert str(e.value) == "Collection name is not provided."


def test_raise_value_error_query(api):
    with pytest.raises(ValueError) as e:
        api.get_data(
            provider_name="osu_provider",
            data_name="wits",
            query="",
            asset_id=123456789,
            read_from_mongo="False",
        )

    assert str(e.value) == "Query is not provided."


def records_func():
    # raed the data from the local location
    path = Path(__file__).parent / ".." / "resources"
    collection_name = "wits"
    with open(path / f"{collection_name}.json", "r") as f:
        records = json.load(f)
        return records


def test_raise_value_error_query_no_sort(api, mocker):

    mocker.patch("src.osu_api.pymongo.collection.Collection.find",
                 side_effect=records_func)
    # mocker.patch.object(Api, "get_data", side_effect=records)

    query = {
        # "sort": -1,
        "limit": 3,
        "fields": ["timestamp", "provider", "drill_string_id", "data"],
    }

    records = api.get_data(
        provider_name="osu_provider",
        data_name="wits",
        query=query,
        asset_id=123456789,
        read_from_mongo="True",
    )

    # check if the records are sorted by timestamp descending order
    assert records[0]["timestamp"] > records[1]["timestamp"]


def test_raise_value_error_query_no_limit(api, mocker):

    mocker.patch("src.osu_api.pymongo.collection.Collection.find",
                 side_effect=records_func)

    query = {
        "sort": -1,
        # "limit": 3,
        "fields": ["timestamp", "provider", "drill_string_id", "data"],
    }

    records = api.get_data(
        provider_name="osu_provider",
        data_name="wits",
        query=query,
        asset_id=123456789,
        read_from_mongo="True",
    )

    # check if the len of records is 10
    assert len(records) == 10
