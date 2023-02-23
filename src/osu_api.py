import json
from pathlib import Path
from typing import Dict


class Api:
    """
    API class
    This api is used to get, put, delete data from a database.
    There is no endpoint is used in this class. The DummyApi class
    reads the data from the local location.
    """

    def __init__(self, *args, **kwargs) -> None:
        self._path: str = kwargs.get(
            "resources_path", Path(__file__).parent / ".." / "resources"
        )

    def get_data(self, *args, **kwargs) -> Dict:
        provider = kwargs.get("provider_name", {})
        if not provider:
            raise ValueError("Provider is not provided.")

        collection_name = kwargs.get("data_name", {})
        if not collection_name:
            raise ValueError("Collection name is not provided.")

        query = kwargs.get("query", {})
        if not query:
            raise ValueError("Query is not provided.")

        sort_ts = query.get("sort", {})
        if not sort_ts:
            sort_ts = -1  # descending order

        limit = query.get("limit", {})
        if not limit:
            limit = 10

        fields = query.get("fields", {})

        # raed the data from the local location
        with open(self._path / f"{collection_name}.json", "r") as f:
            records = json.load(f)

        # check if all fields are present in the query
        if not all(field in records[0] for field in fields):
            # print available fields
            print(f"Available fields are: {records[0].keys()}")
            raise ValueError("\n\nFields are not present in the data.")

        # check if timestamp is present in the query
        if "timestamp" in records[0]:
            # sort the data based on the timestamp
            if sort_ts == -1:
                records = sorted(records, key=lambda x: x["timestamp"], reverse=True)
            else:
                records = sorted(records, key=lambda x: x["timestamp"])

        # filter the data based on the fields
        if fields:
            records = [
                {k: v for k, v in record.items() if k in fields} for record in records
            ]

        # limit the data
        records = records[:limit]
        return records


if __name__ == "__main__":
    api = Api()
    query = {
        "provider_name": "provider_name",
        "sort": -1,
        "limit": 13,
        "fields": ["id", "motor_id", "motor_cof", "type"],
    }
    records = api.get_data(
        data_name="dhm_data", provider_name="provider_name", query=query
    )
    print(records)
