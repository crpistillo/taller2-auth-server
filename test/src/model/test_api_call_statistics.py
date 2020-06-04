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

    def test_quantity_by_call_type(self):
        api_calls = [ApiKeyCall(api_alias="Jenny 1", path="/user", method="GET", status=200, time=1.0,
                                timestamp=datetime.now() - timedelta(days=1)),
                     ApiKeyCall(api_alias="Jenny 1", path="/register", method="POST", status=200, time=2.0,
                                timestamp=datetime.now() - timedelta(days=1)),
                     ApiKeyCall(api_alias="Jenny 1", path="/user", method="POST", status=200, time=2.0,
                                timestamp=datetime.now() - timedelta(days=2)),
                     ApiKeyCall(api_alias="Jenny 1", path="/user", method="GET", status=200, time=2.0,
                                timestamp=datetime.now() - timedelta(days=10)),
                     ApiKeyCall(api_alias="Jenny 1", path="/user", method="POST", status=200, time=10.0,
                                timestamp=datetime.now() - timedelta(days=10)),
                     ApiKeyCall(api_alias="Jenny 1", path="/register", method="POST", status=401, time=20.0,
                                timestamp=datetime.now() - timedelta(days=10)),
                     ApiKeyCall(api_alias="Jenny 1", path="/user", method="POST", status=200, time=20.0,
                                timestamp=datetime.now() - timedelta(days=40)),
                     ApiKeyCall(api_alias="Jenny 2", path="/user", method="POST", status=200, time=1.0,
                                timestamp=datetime.now() - timedelta(days=1)),
                     ]
        statistics = ApiCallsStatistics(api_calls)
        api_calls_by_type = statistics.api_calls_by_type()
        self.assertTrue("Jenny 1" in api_calls_by_type)
        self.assertTrue("Jenny 2" in api_calls_by_type)
        self.assertEqual(2,api_calls_by_type["Jenny 1"][0]["/register"])
        self.assertEqual(5,api_calls_by_type["Jenny 1"][0]["/user"])
