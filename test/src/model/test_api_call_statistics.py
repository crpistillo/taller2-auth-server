import unittest
from src.model.api_calls_statistics import ApiCallsStatistics, ApiKeyCall
from datetime import datetime, timedelta

class TestUnitsPhoto(unittest.TestCase):
    def test_median_response_time_30d(self):
        api_calls = [ApiKeyCall(api_alias="Jenny 1", path="/user", method="POST", status=200, time=1.0,
                                timestamp=datetime.now() - timedelta(days=1)),
                     ApiKeyCall(api_alias="Jenny 1", path="/user", method="POST", status=200, time=2.0,
                                timestamp=datetime.now() - timedelta(days=1)),
                     ApiKeyCall(api_alias="Jenny 1", path="/user", method="POST", status=200, time=2.0,
                                timestamp=datetime.now() - timedelta(days=2)),
                     ApiKeyCall(api_alias="Jenny 1", path="/user", method="POST", status=200, time=2.0,
                                timestamp=datetime.now() - timedelta(days=10)),
                     ApiKeyCall(api_alias="Jenny 1", path="/user", method="POST", status=200, time=10.0,
                                timestamp=datetime.now() - timedelta(days=10)),
                     ApiKeyCall(api_alias="Jenny 1", path="/user", method="POST", status=200, time=20.0,
                                timestamp=datetime.now() - timedelta(days=10)),
                     ApiKeyCall(api_alias="Jenny 1", path="/user", method="POST", status=200, time=20.0,
                                timestamp=datetime.now() - timedelta(days=40)),
                     ApiKeyCall(api_alias="Jenny 2", path="/user", method="POST", status=200, time=1.0,
                                timestamp=datetime.now() - timedelta(days=1)),
                     ]
        statistics = ApiCallsStatistics(api_calls)
        medians_by_day_dict = statistics.median_response_time_last_30_days()
        self.assertTrue("Jenny 1" in medians_by_day_dict)
        self.assertTrue("Jenny 2" in medians_by_day_dict)
        self.assertTrue(1 in medians_by_day_dict["Jenny 1"])
        self.assertTrue(2 in medians_by_day_dict["Jenny 1"])
        self.assertTrue(10 in medians_by_day_dict["Jenny 1"])
        self.assertTrue(1 in medians_by_day_dict["Jenny 2"])
        self.assertEqual(3, len(medians_by_day_dict["Jenny 1"].keys()))
        self.assertEqual(1, len(medians_by_day_dict["Jenny 2"].keys()))
        self.assertEqual(1.5, medians_by_day_dict["Jenny 1"][1])
        self.assertEqual(2.0, medians_by_day_dict["Jenny 1"][2])
        self.assertEqual(10.0, medians_by_day_dict["Jenny 1"][10])
        self.assertEqual(1.0, medians_by_day_dict["Jenny 2"][1])
