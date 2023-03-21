import json
import os
from pathlib import Path
from typing import Dict

import boto3
import pymongo

from src.model import SETTINGS


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

        if kwargs.get("read_from_mongo", "False") == "True":
            # or read from mongoDB
            password = os.getenv("MONGO_PASSWORD")
            username = os.getenv("MONGO_USERNAME")
            myclient = pymongo.MongoClient(
                f"mongodb+srv://{username}:{password}@cluster0.gvlqokj.mongodb.net/?retryWrites=true&w=majority"
            )

            map_database_names = {
                "wits": "wits",
                "dhm_data": "downhole_motor",
                "ds_data": "drillstring",
            }

            mydb = myclient["Drilling"]
            mycol = mydb[map_database_names[collection_name]]

            records = []
            for x in mycol.find():
                records.append(x)

        # for each record in the records, check if all fields are present
        # otherwise raise an error
        for record in records:
            if not all(field in record for field in query["fields"]):
                raise ValueError("Fields are not present in the records.")

        # check if timestamp is present in the query
        if "timestamp" in records[0]:
            # sort the data based on the timestamp
            if sort_ts == -1:
                records = sorted(records, key=lambda x: x["timestamp"], reverse=True)
            else:
                records = sorted(records, key=lambda x: x["timestamp"])

        # filter data based on the timestamp
        ts_min = query.get("ts_min", {})
        ts_max = query.get("ts_max", {})
        if ts_min and ts_max:
            # check both the timestamp are not equal otherwise it rises an error
            if ts_min == ts_max:
                raise ValueError("ts_min and ts_max are equal.")
            records = [
                record for record in records if ts_min <= record["timestamp"] < ts_max
            ]

        # filter the data based on the fields
        if fields:
            records = [
                {k: v for k, v in record.items() if k in fields} for record in records
            ]

        # limit the data
        records = records[:limit]
        return records

    def post_data(self, *args, **kwargs) -> None:
        data = kwargs.get("data", {})
        address = kwargs.get("address", {})
        if not address:
            raise ValueError("Address is not provided.")
        # save data as json at provided address
        with open(address, "w") as f:
            json.dump(data, f, indent=4, sort_keys=False)

        # save the last data in cache
        # with open(self._cache_address, "w") as f:
        #     json.dump(data[-1], f, indent=4, sort_keys=False)

        # save the latest data in the S3
        bucket_name = SETTINGS.CACHE_BUCKET_NAME
        file_name = SETTINGS.CACHE_FILE_NAME
        s3 = boto3.resource(
            service_name="s3",
            region_name=SETTINGS.CACHE_REGION_NAME,
            aws_access_key_id=os.getenv("S3_AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("S3_AWS_SECRET_ACCESS_KEY"),
        )

        s3.Object(bucket_name, file_name).put(Body=json.dumps(data[-1]))


if __name__ == "__main__":
    api = Api()
    query = {
        "provider_name": "provider_name",
        "sort": 1,
        "limit": 20,
        "fields": ["timestamp", "provider", "drill_string_id", "data", "activity"],
        "ts_min": 1677112070,
        "ts_max": 1677112080,
    }
    records = api.get_data(data_name="wits", provider_name="provider_name", query=query)
    print(records)
