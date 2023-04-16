import json
import os
from typing import Dict

import boto3


def post_data_to_s3(_data: Dict = None, bucket_name: str = None, file_name: str = None):
    bucket_name = bucket_name or "bgapptestdemo"
    file_name = file_name or "cache.json"
    s3 = boto3.resource(
        service_name="s3",
        region_name="us-east-2",
        aws_access_key_id=os.getenv("S3_AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("S3_AWS_SECRET_ACCESS_KEY"),
    )
    s3.Object(bucket_name, file_name).put(Body=json.dumps(_data))
    # read the file from the bucket again and print the _data
    s3_object = s3.Object(bucket_name, file_name).get()
    # the _data in body is in json format
    _data = s3_object["Body"].read().decode("utf-8")
    _data = json.loads(_data)
    print(_data)


if __name__ == "__main__":
    # write a following dict into the bucket
    cahce_data = {
        "id": "92a6e03f-ece0-4b59-b960-3fc8997aebda",
        "timestamp": 1677115017,
        "provider": "osu_provider",
        "drillstring_id": "ds_1",
        "data": {"bg": 0},
    }
    post_data_to_s3(
        _data=cahce_data, bucket_name="bgapptestdemo", file_name="cache.json"
    )

    # write the settings into the s3
    app_setting_data = {
        "asset_id": 123456789,
        "data": {
            "bit_wear_constant": 3_000_000_000_000,
        },
    }
    post_data_to_s3(
        _data=app_setting_data,
        bucket_name="bgapptestdemo",
        file_name="app_setting.json",
    )
