import json
import os
import uuid
from itertools import groupby
from pathlib import Path
from typing import Dict, List, Optional

import boto3

from src.enums import BGAppTasks
from src.model import (SETTINGS, BitGrade, BitGradeData, DownholeMotor,
                       DrillSting, Wits)
from src.osu_api import Api

BIT_WEAR_CONSTANT = 3_000_000_000_000


class BGApp:
    """
    This is a class for the ROPApp.
    """

    def __init__(self, api: Api, event: Dict) -> None:
        self._api = api
        self._event = event
        self._asset_id = event.get("asset_id", None)
        self._event_task = event.get("task", None)

    def run(self) -> Optional[Dict]:
        if self._event_task == BGAppTasks.CALCULATE_BG.value:
            item_needed = BGAppTasks.CALCULATE_BG.items_needed
            # check if all ITEMS_NEEDED_TO_CALCULATE_BG are present in the event
            if not all(item in self._event for item in item_needed):
                raise ValueError(f"Missing items in the event: {item_needed}")
            self.calculate_BG()
        elif self._event_task == BGAppTasks.RETURN_CACHE.value:
            item_needed = BGAppTasks.RETURN_CACHE.items_needed
            # check if all ITEMS_NEEDED_TO_RETURN_CACHE are present in the event
            if not all(item in self._event for item in item_needed):
                raise ValueError(f"Missing items in the event: {item_needed}")
            cache = self.return_cache()
            return cache
        elif self._event_task == BGAppTasks.DELETE_CACHE.value:
            item_needed = BGAppTasks.DELETE_CACHE.items_needed
            # check if all ITEMS_NEEDED_TO_RETURN_BG are present in the event
            if not all(item in self._event for item in item_needed):
                raise ValueError(f"Missing items in the event: {item_needed}")
            self.delete_cache()
        else:
            raise ValueError(f"Invalid task: {self._event_task}")

    def get_wits_data(self) -> Dict:
        start_ts = self._event["start_ts"]
        end_ts = self._event["end_ts"]

        query = {
            "sort": 1,
            # "limit": 3,
            "fields": [
                "timestamp",
                "provider",
                "drill_string_id",
                "data",
                "activity",
            ],
            "ts_min": start_ts,
            "ts_max": end_ts,
        }
        records = self._api.get_data(
            provider_name=SETTINGS.PROVIDER,
            data_name=SETTINGS.WITS_COLLECTION,
            query=query,
            asset_id=self._asset_id,
        )

        parsed_wits_records = [
            Wits.parse_wits(record)
            for record in records
            if Wits.check_fields(record) and Wits.check_activity(record)
        ]

        return parsed_wits_records

    def get_ds_data(self) -> Dict:
        query = {
            "fields": ["_drill_string_id", "down_hole_motor_id"],
        }
        records = self._api.get_data(
            provider_name=SETTINGS.PROVIDER,
            data_name=SETTINGS.DRILL_STRING_COLLECTION,
            query=query,
            asset_id=self._asset_id,
        )
        ds_records = [DrillSting(**record) for record in records]
        return ds_records

    def get_downhole_motor_data(self) -> Dict:
        query = {
            "fields": ["motor_id", "motor_cof"],
        }
        records = self._api.get_data(
            provider_name=SETTINGS.PROVIDER,
            data_name=SETTINGS.DOWN_HOLE_MOTOR_COLLECTION,
            query=query,
            asset_id=self._asset_id,
        )
        dhm_records = [DownholeMotor(**record) for record in records]

        return dhm_records

    def calculate_BG(self, _return=False) -> List:
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

        bg_list = self.calculate_bit_grade(
            parsed_wits_records_per_ds, ds_dhm_cof_map, _return=_return
        )
        if _return:
            return bg_list

    def return_cache(self):
        bucket_name = "bgapptestdemo"
        file_name = "cache.json"
        s3 = boto3.resource(
            service_name="s3",
            region_name="us-east-2",
            aws_access_key_id=os.getenv("S3_AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("S3_AWS_SECRET_ACCESS_KEY"),
        )
        # read the file from the bucket again and print the data
        s3_object = s3.Object(bucket_name, file_name).get()
        # the data in body is in json format
        data = s3_object["Body"].read().decode("utf-8")
        data = json.loads(data)
        # print(data)
        return data

    def delete_cache(self):
        bucket_name = "bgapptestdemo"
        file_name = "cache.json"
        s3 = boto3.resource(
            service_name="s3",
            region_name="us-east-2",
            aws_access_key_id=os.getenv("S3_AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("S3_AWS_SECRET_ACCESS_KEY"),
        )
        # if the file exists, delete it and print a message
        s3.Object(bucket_name, file_name).delete()
        print("File deleted")

    def calculate_bit_grade(
        self, parsed_wits_records_per_ds: Dict, ds_dhm_cof_map: Dict, _return=False
    ) -> Dict:
        for ds, wits_records in parsed_wits_records_per_ds.items():
            # get the motor_cof for the drill_string_id
            motor_cof = ds_dhm_cof_map[ds]

            # calculate the bit_grade for each wits record
            bit_grade_records = [
                self.bit_grade_model(
                    wits_record.wob,
                    wits_record.rpm,
                    motor_cof,
                    wits_record.flowrate,
                )
                for wits_record in wits_records
            ]

            # make bit_grade_records cumulative
            cumulative_bit_grade_records = [
                sum(bit_grade_records[: i + 1]) for i in range(len(bit_grade_records))
            ]

            # check the cache for the latest bit_grade for the drill_string_id
            # path = Path(__file__).parent / ".." / "resources" / "calculated_bg"
            # filename = "cache.json"
            # address = path / filename

            # with open(address, "r") as f:
            #     cache = json.load(f)
            bucket_name = SETTINGS.CACHE_BUCKET_NAME
            file_name = SETTINGS.CACHE_FILE_NAME
            s3 = boto3.resource(
                service_name="s3",
                region_name=SETTINGS.CACHE_REGION_NAME,
                aws_access_key_id=os.getenv("S3_AWS_ACCESS_KEY"),
                aws_secret_access_key=os.getenv("S3_AWS_SECRET_ACCESS_KEY"),
            )
            s3_object = s3.Object(bucket_name, file_name).get()
            cache = s3_object["Body"].read().decode("utf-8")
            cache = json.loads(cache)
            # if cache is not emmpy
            if cache:
                cache_ds = cache.get("drillstring_id")
                cache_bg = cache.get("data").get("bg")

                if ds == cache_ds:
                    # add the value of the latest bit_grade to the current bit_grade
                    cumulative_bit_grade_records = [
                        bit_grade_record + cache_bg
                        for bit_grade_record in cumulative_bit_grade_records
                    ]

            # round the bit_grade values to 2 decimal places
            cumulative_bit_grade_records = [
                round(bit_grade_record, 3)
                for bit_grade_record in cumulative_bit_grade_records
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
            if _return:
                return bit_grade_list

    @staticmethod
    def bit_grade_model(wob, rpm, flowrate, motor_cof):
        bg = wob * (rpm + flowrate * motor_cof) / BIT_WEAR_CONSTANT
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
    end_ts = 1677115068  # this the final wits timestamp

    # empty the bg_data.json file in the resources/calculated_bg folder
    path = Path(__file__).parent / ".." / "resources" / "calculated_bg"
    filename = "bg_data.json"
    address = path / filename
    with open(address, "w") as f:
        json.dump([], f)

    # make batch events between start_ts and end_ts with 60 seconds interval
    # and call the rop_app.get_wits_data() method for each batch event and print the records
    for i in range(start_ts, end_ts, 60):
        _end_ts = i + 60
        # check if i + 5 is less than end_ts
        if i + 60 > end_ts:
            _end_ts = end_ts
        event = {"start_ts": i, "end_ts": _end_ts, "asset_id": 123456789}
        # print(event)
        bg_app = BGApp(api, event)
        bg_app.run()
        # print(records)
        # sleep for 5 second
        # time.sleep(1)
