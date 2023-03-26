import json
import os

import boto3

if __name__ == "__main__":
    bucket_name = "bgapptestdemo"
    file_name = "cache.json"
    s3 = boto3.resource(
        service_name="s3",
        region_name="us-east-2",
        aws_access_key_id=os.getenv("S3_AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("S3_AWS_SECRET_ACCESS_KEY"),
    )

    # check if the file exists in the bucket
    # s3.Object(bucket_name, file_name).load()

    # if the file exists, delete it and print a message
    # s3.Object(bucket_name, file_name).delete()
    # print(f"{file_name} deleted from {bucket_name}")

    # write a following dict into the bucket
    data = {
        "id": "92a6e03f-ece0-4b59-b960-3fc8997aebda",
        "timestamp": 1677115017,
        "provider": "osu_provider",
        "drillstring_id": "ds_1",
        "data": {"bg": 0},
    }
    s3.Object(bucket_name, file_name).put(Body=json.dumps(data))
    print(f"{file_name} written to {bucket_name}")

    # read the file from the bucket again and print the data
    s3_object = s3.Object(bucket_name, file_name).get()
    # the data in body is in json format
    data = s3_object["Body"].read().decode("utf-8")
    data = json.loads(data)
    print(data)
