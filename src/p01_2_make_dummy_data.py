import json
import random
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from src.enums import Activities


class GenerateDummyData:
    """
    Generate data for the project.
    """

    def __init__(self, *args, **kwargs):
        curr_dt: datetime = datetime.now()
        self.curr_ts: int = int(round(curr_dt.timestamp()))

    @staticmethod
    def _generate_records(**kwargs) -> List[Dict[str, Any]]:
        """
        Generate records for the project.
        :param kwargs:
        mds is measured depth in meters, wob is weight on bit in lbf,
        rpm is revolutions per minute, rop is rate of penetration in ft per minute.
        :return:
        """
        number_of_datapoints: int = kwargs.get("number_of_datapoints", 1000)

        start_ts = kwargs.get("start_ts", 1677112068)

        mds_min: float = kwargs.get("mds_min", 0)
        mds_max: float = kwargs.get("mds_max", 10_000)
        wob_min: float = kwargs.get("wob_min", 0)
        wob_max: float = kwargs.get("wob_max", 50_000)
        rpm_min: float = kwargs.get("rpm_min", 0)
        rpm_max: float = kwargs.get("rpm_max", 350)
        rop_min: float = kwargs.get("rop_min", 0)
        rop_max: float = kwargs.get("rop_max", 300)
        flowrate_min: float = kwargs.get("mds_min", 0)
        flowrate_max: float = kwargs.get("mds_max", 500)

        drill_string_id: str = kwargs.get("drill_string_id", "ds_1")

        # mds is increased each data point.
        mds: np.ndarray = np.linspace(mds_min, mds_max, number_of_datapoints + 1)
        wobs: np.ndarray = np.random.uniform(wob_min, wob_max, number_of_datapoints + 1)
        rpms: np.ndarray = np.random.uniform(rpm_min, rpm_max, number_of_datapoints + 1)
        rops: np.ndarray = np.random.uniform(rop_min, rop_max, number_of_datapoints + 1)
        flowrates: np.ndarray = np.random.uniform(
            flowrate_min, flowrate_max, number_of_datapoints + 1
        )

        timestamps: List[int] = [
            start_ts + i for i in range(1, number_of_datapoints + 1)
        ]
        ids: List[str] = [str(uuid.uuid4()) for _ in range(1, number_of_datapoints + 1)]

        # use Activity enum to make random activity.
        activities: List[str] = [
            random.choice(list(Activities)).value
            for _ in range(1, number_of_datapoints + 1)
        ]

        records: List[Dict[str, Any]] = [
            {
                "id": id,
                "timestamp": ts,
                "provider": "osu_provider",
                "drill_string_id": drill_string_id,
                "asset_id": 123456789,
                "data": {
                    "md": round(md, 3),
                    "wob": round(wob, 3),
                    "rpm": round(rpm, 3),
                    "rop": round(rop, 3),
                    "flowrate": round(flowrate, 3),
                },
                "activity": activity,
            }
            for id, ts, md, wob, rpm, rop, flowrate, activity in zip(
                ids, timestamps, mds, wobs, rpms, rops, flowrates, activities
            )
        ]
        return records

    @staticmethod
    def generate_records_and_save_data(**kwargs) -> None:
        _path = kwargs.get("path", Path(__file__).parent / ".." / "resources")
        file_name = kwargs.get("file_name", "data.json")
        records = GenerateDummyData._generate_records(**kwargs)
        with open(_path / file_name, "w") as f:
            json.dump(records, f, indent=4, sort_keys=False)

    @staticmethod
    def combine_json_files(**kwargs) -> None:
        """
        Combine json files.
        :param kwargs:
        :return:
        """
        _path = kwargs.get("path", Path(__file__).parent / ".." / "resources")
        file_names = kwargs.get(
            "file_names", ["wits_ds_1.json", "wits_ds_2.json", "wits_ds_3.json"]
        )
        combined_file_name = kwargs.get("combined_file_name", "data_combined.json")
        records = []
        for file_name in file_names:
            with open(_path / file_name, "r") as f:
                records.extend(json.load(f))
        with open(_path / combined_file_name, "w") as f:
            json.dump(records, f, indent=4, sort_keys=False)

    @staticmethod
    def make_ds_data(**kwargs) -> None:
        """
        Make data for drill string. This method is used to generate some
        dummy data with drillstring id, down hole-motor_id, etc.
        :param kwargs:
        :return:
        """
        _path = kwargs.get("path", Path(__file__).parent / ".." / "resources")
        file_name = kwargs.get("file_name", "ds_data.json")
        number_of_ds = kwargs.get("number_of_datapoints", 3)
        ids: List[str] = [str(uuid.uuid4()) for _ in range(1, number_of_ds + 1)]
        ds_ids = [f"ds_{i}" for i in range(1, number_of_ds + 1)]
        down_hole_motor_ids: List[str] = [
            f"motor_id_{i}" for i in range(1, number_of_ds + 1)
        ]
        records: List[Dict[str, Any]] = [
            {
                "id": id,
                "_drill_string_id": ds_id,
                "down_hole_motor_id": dhm_id,
            }
            for id, ds_id, dhm_id in zip(ids, ds_ids, down_hole_motor_ids)
        ]
        with open(_path / file_name, "w") as f:
            json.dump(records, f, indent=4, sort_keys=False)

    @staticmethod
    def make_dhm_data(**kwargs) -> None:
        """
        Make data for down hole motor. This method is used to generate some
        dummy data with drillstring id, down hole-motor_id, etc.
        :param kwargs:
        :return:
        """
        _path = kwargs.get("path", Path(__file__).parent / ".." / "resources")
        file_name = kwargs.get("file_name", "dhm_data.json")
        number_of_dhm = kwargs.get("number_of_datapoints", 3)
        ids: List[str] = [str(uuid.uuid4()) for _ in range(1, number_of_dhm + 1)]
        dhm_ids = [f"motor_id_{i}" for i in range(1, number_of_dhm + 1)]
        motor_cof_min: float = kwargs.get("mds_min", 0)
        motor_cof_max: float = kwargs.get("mds_max", 500)
        motor_cofs: np.ndarray = np.random.uniform(
            motor_cof_min, motor_cof_max, number_of_dhm + 1
        )
        records: List[Dict[str, Any]] = [
            {
                "id": id,
                "motor_id": dhm_id,
                "motor_cof": motor_cof,
                "type": "positive_displacement",
            }
            for id, motor_cof, dhm_id in zip(ids, motor_cofs, dhm_ids)
        ]
        with open(_path / file_name, "w") as f:
            json.dump(records, f, indent=4, sort_keys=False)


if __name__ == "__main__":
    # set seed for reproducibility
    np.random.seed(42)
    START_TIMESTAMP = 1677112068
    NUMBER_OF_DATAPOINTS = 1000

    obj = GenerateDummyData()

    obj.generate_records_and_save_data(
        file_name="wits_ds_1.json",
        number_of_datapoints=NUMBER_OF_DATAPOINTS,
        drill_string_id="ds_1",
        start_ts=START_TIMESTAMP,
        mds_min=0,
        mds_max=10_000,
    )
    START_TIMESTAMP += NUMBER_OF_DATAPOINTS
    obj.generate_records_and_save_data(
        file_name="wits_ds_2.json",
        number_of_datapoints=NUMBER_OF_DATAPOINTS,
        drill_string_id="ds_2",
        start_ts=START_TIMESTAMP,
        mds_min=10_000,
        mds_max=20_000,
    )
    START_TIMESTAMP += NUMBER_OF_DATAPOINTS
    obj.generate_records_and_save_data(
        file_name="wits_ds_3.json",
        number_of_datapoints=NUMBER_OF_DATAPOINTS,
        drill_string_id="ds_3",
        start_ts=START_TIMESTAMP,
        mds_min=20_000,
        mds_max=30_000,
    )
    obj.combine_json_files(
        combined_file_name="wits.json",
        file_names=["wits_ds_1.json", "wits_ds_2.json", "wits_ds_3.json"],
    )

    obj.make_ds_data()

    obj.make_dhm_data()
