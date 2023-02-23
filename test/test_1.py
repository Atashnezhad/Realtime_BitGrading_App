import unittest
from src.osu_api import Api
from pathlib import Path


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
