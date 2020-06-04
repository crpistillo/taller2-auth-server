from create_application import create_application
import unittest
import os
from src.model.api_key import ApiKey
from datetime import datetime, timedelta
import json

class TestFlaskDummy(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["API_GENERATOR_SECRET"] = "secret string"
        self.app, self.controller = create_application(return_controller=True)
        api_key1 = ApiKey("Jenny 1", "dumb")
        api_key2 = ApiKey("Jenny 2", "dumb")
        self.controller.database.save_api_key(api_key1)
        self.controller.database.save_api_key(api_key2)
        for i in range(40):
            self.controller.database.register_api_call(api_key1.get_api_key_hash(), "/user", "GET" if i%2 == 0 else "POST", 200, 0.1*i,
                                                       datetime.now()-timedelta(days=i))
        for i in range(40):
            self.controller.database.register_api_call(api_key2.get_api_key_hash(), "/user", "GET" if i%2 == 0 else "POST", 200, 0.1*i,
                                                       datetime.now()-timedelta(days=i))
        self.app.testing = True

    def test_render_statistics(self):
        with self.app.test_client() as c:
            response = c.get('/server_statistics')
            self.assertEqual(response.status_code, 200)
            for i in range(30):
                self.assertTrue(("%d" % i) in response.data.decode())
                self.assertTrue(("%.1f" % (0.1*10)) in response.data.decode())