import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import numpy as np


class GenerateData:
    """
    Generate data for the project.
    """

    def __init__(self, *args, **kwargs):
        curr_dt: datetime = datetime.now()
        self.curr_ts: int = int(round(curr_dt.timestamp()))

    def generate_records(self, **kwargs) -> List[Dict[str, Any]]:
        number_of_datapoints: int = kwargs.get("number_of_datapoints", 1000)
        wob_min: float = kwargs.get("wob_min", 0)
        wob_max: float = kwargs.get("wob_max", 50_000)
        rpm_min: float = kwargs.get("rpm_min", 0)
        rpm_max: float = kwargs.get("rpm_max", 350)
        rop_min: float = kwargs.get("rop_min", 0)
        rop_max: float = kwargs.get("rop_max", 300)
        wobs: np.ndarray = np.random.uniform(wob_min, wob_max, number_of_datapoints)
        rpms: np.ndarray = np.random.uniform(rpm_min, rpm_max, number_of_datapoints)
        rops: np.ndarray = np.random.uniform(rop_min, rop_max, number_of_datapoints)
        timestamps: List[int] = [self.curr_ts + i for i in range(1, number_of_datapoints)]
        ids: List[str] = [str(uuid.uuid4()) for _ in range(1, number_of_datapoints)]
        records: List[Dict[str, Any]] = [
            {
                "id": id,
                "timestamp": ts,
                "provider": "provider_name",
                "data": {"wob": round(wob, 3), "rpm": round(rpm, 3), "rop": round(rop, 3)},
            }
            for id, ts, wob, rpm, rop in zip(ids, timestamps, wobs, rpms, rops)
        ]
        return records

    def save_data(self, **kwargs) -> None:
        _path = kwargs.get("path", Path(__file__).parent / ".." / "resources")
        file_name = kwargs.get("file_name", "data.json")
        records = self.generate_records()
        with open(_path / file_name, "w") as f:
            json.dump(records, f, indent=4, sort_keys=False)


if __name__ == "__main__":

    obj = GenerateData()
    obj.generate_records()
    obj.save_data()