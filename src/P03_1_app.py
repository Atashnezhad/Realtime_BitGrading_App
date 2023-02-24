import json
import uuid
from itertools import groupby
from pathlib import Path
from typing import Dict, List

from src.model import BitGrade, BitGradeData, DownholeMotor, DrillSting, Wits
from src.osu_api import Api

NEW_PARAMETER_CONSTANT = 1_000_000_000_000


class BGApp:
    """
    This is a class for the ROPApp.
    """

    def __init__(self, api: Api, event: Dict) -> None:
        self._api = api
        self._event = event

    def get_wits_data(self) -> Dict:
        start_ts = self._event["start_ts"]
        end_ts = self._event["end_ts"]

        query = {
            "sort": 1,
            # "limit": 3,
            "fields": ["id", "timestamp", "provider", "drill_string_id", "data"],
            "ts_min": start_ts,
            "ts_max": end_ts,
        }
        records = self._api.get_data(
            provider_name="osu_provider",
            data_name="wits",
            query=query,
        )

        parsed_wits_records = [
            Wits.parse_wits(record) for record in records if Wits.check_fields(record)
        ]

        return parsed_wits_records

    def get_ds_data(self) -> Dict:
        query = {
            "fields": ["_drill_string_id", "down_hole_motor_id"],
        }
        records = self._api.get_data(
            provider_name="osu_provider",
            data_name="ds_data",
            query=query,
        )
        ds_records = [DrillSting(**record) for record in records]
        return ds_records

    def get_downhole_motor_data(self) -> Dict:
        query = {
            "fields": ["motor_id", "motor_cof"],
        }
        records = self._api.get_data(
            provider_name="osu_provider",
            data_name="dhm_data",
            query=query,
        )
        dhm_records = [DownholeMotor(**record) for record in records]

        return dhm_records

    def run(self) -> None:
        parsed_wits_records = self.get_wits_data()
        # group the records based on the drill_string_id
        parsed_wits_records_per_ds = {
            k: list(v)
            for k, v in groupby(parsed_wits_records, key=lambda x: x.drill_string_id)
        }
        ds_records = self.get_ds_data()
        dhm_records = self.get_downhole_motor_data()

        # get corresponding motor_coefs for each drill_string_id and save it in a dict
        ds_dhm_cof_map = {
            ds.drill_string_id: dhm.motor_cof
            for ds in ds_records
            for dhm in dhm_records
            if ds.down_hole_motor_id == dhm.motor_id
        }

        self.calculate_bit_grade(parsed_wits_records_per_ds, ds_dhm_cof_map)

    def calculate_bit_grade(
        self, parsed_wits_records_per_ds: Dict, ds_dhm_cof_map: Dict
    ) -> Dict:
        for ds, wits_records in parsed_wits_records_per_ds.items():
            # get the motor_cof for the drill_string_id
            motor_cof = ds_dhm_cof_map[ds]

            # calculate the bit_grade for each wits record
            bit_grade_records = [
                self.bit_grade_model(
                    wits_record.wob, wits_record.rpm, motor_cof, wits_record.flowrate
                )
                for wits_record in wits_records
            ]

            # make bit_grade_records cumulative
            cumulative_bit_grade_records = [
                round(sum(bit_grade_records[: i + 1]), 3)
                for i in range(len(bit_grade_records))
            ]

            bg_data_list = [
                BitGradeData(
                    bg=cumulative_bit_grade_record,
                )
                for cumulative_bit_grade_record in cumulative_bit_grade_records
            ]

            bit_grade_list = [
                BitGrade(
                    id=BGApp.make_dummy_id(),
                    timestamp=wits_record.timestamp,
                    provider="osu_provider",
                    drillstring_id=ds,
                    data=bg_data,
                )
                for wits_record, bg_data in zip(wits_records, bg_data_list)
            ]

            bit_grade_list = [case.dict() for case in bit_grade_list]
            # save the bit_grade records in the database
            self.post_bg(bit_grade_list)

    @staticmethod
    def bit_grade_model(wob, rpm, flowrate, motor_cof):
        bg = wob * (rpm + flowrate * motor_cof) / NEW_PARAMETER_CONSTANT
        return bg

    @staticmethod
    def make_dummy_id():
        return str(uuid.uuid4())

    def post_bg(self, data: List[BitGrade]) -> None:
        path = Path(__file__).parent / ".." / "resources" / "calculated_bg"
        # if path does not exist, create it
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        filename = "bg_data.json"
        address = path / filename
        # if file is available, read it and append the new data to it
        if address.exists():
            with open(address, "r") as f:
                data = json.load(f) + data

        self._api.post_data(address=address, data=data)


if __name__ == "__main__":
    api = Api()
    start_ts = 1677112070
    end_ts = 1677112083
    # make batch events between start_ts and end_ts with 5 seconds interval
    # and call the rop_app.get_wits_data() method for each batch event and print the records
    for i in range(start_ts, end_ts, 5):
        _end_ts = i + 5
        # check if i + 5 is less than end_ts
        if i + 5 > end_ts:
            _end_ts = end_ts
        event = {"start_ts": i, "end_ts": _end_ts}
        # print(event)
        rop_app = BGApp(api, event)
        rop_app.run()
        # print(records)
        # sleep for 5 second
        # time.sleep(1)
