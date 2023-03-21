import json

import requests

url = "https://data.mongodb-api.com/app/data-otbca/endpoint/data/v1/action/findOne"

payload = json.dumps(
    {
        "collection": "wits",
        "database": "Drilling",
        "dataSource": "Cluster0",
        "filter": {"drill_string_id": "ds_3", "data.md": {"$gt": 21000}},
    }
)

headers = {
    "Content-Type": "application/json",
    "Access-Control-Request-Headers": "*",
    "api-key": "Pqrwqsh6O4HwIPAdBWybJlyoBrpGT8WqTk4Dywqf1luXYyLCLm13ZjumhqA6Ae3e",
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
