import time
from typing import Dict

from src.osu_api import Api


class ROPApp:
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
        return records

    def run(self) -> None:
        pass


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
        rop_app = ROPApp(api, event)
        records = rop_app.get_wits_data()
        print(records)
        # sleep for 5 second
        time.sleep(1)
