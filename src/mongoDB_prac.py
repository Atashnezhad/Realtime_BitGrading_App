import os
from typing import Dict

import pymongo
import requests


def mongo(url: str, headers: Dict, payload: Dict) -> None:
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    print("++++++++++++++++++++++++++++++\n")


if __name__ == "__main__":
    # url = "https://data.mongodb-api.com/app/data-otbca/endpoint/data/v1/action/findOne"
    # headers = {
    #     "Content-Type": "application/json",
    #     "Access-Control-Request-Headers": "*",
    #     "api-key": "Pqrwqsh6O4HwIPAdBWybJlyoBrpGT8WqTk4Dywqf1luXYyLCLm13ZjumhqA6Ae3e",
    # }
    # payload = json.dumps(
    #     {
    #         "collection": "wits",
    #         "database": "Drilling",
    #         "dataSource": "Cluster0",
    #         "filter": {"drill_string_id": "ds_3", "data.md": {"$gt": 21000}},
    #     }
    # )
    #
    # mongo(url, headers, payload)

    password = os.getenv("MONGO_PASSWORD")
    username = os.getenv("MONGO_USERNAME")

    myclient = pymongo.MongoClient(
        f"mongodb+srv://{username}:{password}@cluster0.gvlqokj.mongodb.net/?retryWrites=true&w=majority",
        # connectTimeoutMS=30000
    )

    map_database_names = {
        "wits": "wits",
        "dhm_data": "downhole_motor",
        "ds_data": "drillstring",
        "BG": "BG",
    }

    collection_name = "wits"
    mydb = myclient["Drilling"]
    mycol = mydb[map_database_names[collection_name]]

    records = []
    query = {
        "$and": [
            {"timestamp": {"$gt": 1677112070}},
            {"timestamp": {"$lt": 1677112093}},
        ]
    }

    # Define the projection
    fields = {
        "timestamp": 1,
        "data": 1,
        "drill_string_id": 1,
        "items.product": 1,
        "_id": 0,
    }

    # Define the sort order
    sort_order = [("timestamp", pymongo.DESCENDING)]

    for x in mycol.find(query, fields).sort(sort_order).limit(10):
        records.append(x)
    print(records)
