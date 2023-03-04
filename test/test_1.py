import time
import unittest
from pathlib import Path

from src.osu_api import Api
from src.p03_1_app import BGApp


class Test1(unittest.TestCase):
    def setUp(self) -> None:
        self.resources_path = Path(__file__).parent / ".." / "resources"
        self.api = Api(resources_path=self.resources_path)

    def test_api(self):
        query = {
            "sort": -1,
            "limit": 3,
            "fields": ["id", "timestamp", "provider", "drill_string_id", "data"],
        }
        records = self.api.get_data(
            provider_name="osu_provider",
            data_name="wits",
            query=query,
        )

        # assert the length of the records is 3
        self.assertEqual(len(records), 3)
        # assert the timestamp is sorted in descending order
        self.assertTrue(
            all(
                records[i]["timestamp"] >= records[i + 1]["timestamp"]
                for i in range(len(records) - 1)
            )
        )
        # assert the fields are present in the records
        self.assertTrue(
            all(all(field in record for field in query["fields"]) for record in records)
        )

    def test_bg_app_get_wits_data(self):
        api = Api()
        start_ts = 1677112070
        end_ts = 1677112083
        # make batch events between start_ts and end_ts with 60 seconds interval
        # and call the rop_app.get_wits_data() method for each batch event and print the records
        for i in range(start_ts, end_ts, 60):
            _end_ts = i + 60
            # check if i + 5 is less than end_ts
            if i + 60 > end_ts:
                _end_ts = end_ts
            event = {"start_ts": i, "end_ts": _end_ts}
            # print(event)
            bg_app = BGApp(api, event)
            records = bg_app.get_wits_data()
            print(records)
            # sleep for 5 second
            time.sleep(1)

    def test_bg_app_run(self):
        """
        In this test, we mock the get data and post data and bypass the Api call.
        Note that in fact there is not Api call (because it is fake, and we read the data from the local file).
        But for sack of practice, we still mock the Api call.
        """
        pass
