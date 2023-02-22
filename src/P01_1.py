import json
import uuid
from datetime import datetime
from pathlib import Path

import numpy as np

if __name__ == "__main__":
    # create some data randomly.
    number_of_datapoints = 1000
    wobs = np.random.uniform(0, 50_000, number_of_datapoints)
    rpms = np.random.uniform(0, 350, number_of_datapoints)
    rops = np.random.uniform(0, 300, number_of_datapoints)
    # make timestamps
    curr_dt = datetime.now()
    curr_ts = int(round(curr_dt.timestamp()))
    timestamps = [curr_ts + i for i in range(1, number_of_datapoints)]

    # make random dummy id
    ids = [str(uuid.uuid4()) for _ in range(1, number_of_datapoints)]

    records = [
        {
            "id": id,
            "timestamp": ts,
            "provider": "provider_name",
            "data": {"wob": wob, "rpm": rpm, "rop": rop},
        }
        for id, ts, wob, rpm, rop in zip(ids, timestamps, wobs, rpms, rops)
    ]

    # save the data in the resources' folder.
    # check the path to the resources' folder exists and create it if not.
    path = Path(__file__).parent / ".." / "resources"
    if not path.exists():
        path.mkdir()
    # save the data in the resources' folder as json.
    with open(path / "data.json", "w") as f:
        json.dump(records, f, indent=4, sort_keys=False)
