import json
from pathlib import Path

import pytest

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
    mocker.patch(
        "src.osu_api.pymongo.collection.Collection.find", side_effect=records_func
    )
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


def test_raise_value_error_query_sort_asc(api, mocker):
    mocker.patch(
        "src.osu_api.pymongo.collection.Collection.find", side_effect=records_func
    )
    # mocker.patch.object(Api, "get_data", side_effect=records)

    query = {
        "sort": 1,
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
    assert records[0]["timestamp"] < records[1]["timestamp"]


def test_raise_value_error_query_no_limit(api, mocker):
    mocker.patch(
        "src.osu_api.pymongo.collection.Collection.find", side_effect=records_func
    )

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


def not_all_fields():
    # raed the data from the local location
    path = Path(__file__).parent / ".." / "resources"
    collection_name = "wits_not_all_fields_present"
    with open(path / f"{collection_name}.json", "r") as f:
        records = json.load(f)
        return records


def test_raise_value_error_not_all_fields_present(api, mocker):
    mocker.patch(
        "src.osu_api.pymongo.collection.Collection.find", side_effect=not_all_fields
    )

    with pytest.raises(ValueError) as e:
        query = {
            "sort": -1,
            # "limit": 3,
            "fields": ["timestamp", "provider", "drill_string_id", "data"],
        }

        api.get_data(
            provider_name="osu_provider",
            data_name="wits",
            query=query,
            asset_id=123456789,
            read_from_mongo="True",
        )

        assert str(e.value) == "Not all fields are present in the records."


def test_ts_min_max_eq(api, mocker):
    mocker.patch(
        "src.osu_api.pymongo.collection.Collection.find", side_effect=records_func
    )

    with pytest.raises(ValueError) as e:
        query = {
            "sort": -1,
            # "limit": 3,
            "fields": ["timestamp", "provider", "drill_string_id", "data"],
            "ts_min": 123456789,
            "ts_max": 123456789,
        }

        api.get_data(
            provider_name="osu_provider",
            data_name="wits",
            query=query,
            asset_id=123456789,
            read_from_mongo="True",
        )

        assert str(e.value) == "ts_min and ts_max are equal."


def test_query_with_ts_min_max(api, mocker):
    mocker.patch(
        "src.osu_api.pymongo.collection.Collection.find", side_effect=records_func
    )

    query = {
        "sort": -1,
        "limit": 11,
        "fields": ["timestamp", "provider", "drill_string_id", "data"],
        "ts_min": 1677112069,
        "ts_max": 1677112079,
    }

    records = api.get_data(
        provider_name="osu_provider",
        data_name="wits",
        query=query,
        asset_id=123456789,
        read_from_mongo="True",
    )

    assert len(records) == 10
    # check if the records timestamp is between ts_min and ts_max for all records
    for record in records:
        assert record["timestamp"] >= 1677112069
        assert record["timestamp"] <= 1677112079


def test_post(api, query, mocker):
    # module class module class method!
    mongodb_find_mocker = mocker.patch(
        "src.osu_api.pymongo.collection.Collection.find", side_effect=records_func
    )
    mongodb_insert_many_mocker = mocker.patch(
        "src.osu_api.pymongo.collection.Collection.insert_many", return_value=None
    )

    records = api.get_data(
        provider_name="osu_provider",
        data_name="wits",
        query=query,
        asset_id=123456789,
        read_from_mongo="True",
    )

    api.post_data(data=records)
    mongodb_find_mocker.assert_called_once()
    # assert that the insert_many method is called
    mongodb_insert_many_mocker.assert_called_once()
