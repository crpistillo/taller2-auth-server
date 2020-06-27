from create_application import create_application
import unittest
import os
import json

class TestFlaskDummy(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["API_GENERATOR_SECRET"] = "secret string"
        self.app = create_application()
        self.app.testing = True

    def test_api_health(self):
        with self.app.test_client() as c:
            response = c.get('/health')
            self.assertEqual(response.status_code, 200)
