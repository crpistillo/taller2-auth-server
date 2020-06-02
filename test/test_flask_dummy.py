from create_application import create_application
import unittest
import os
import json

class TestFlaskDummy(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["API_GENERATOR_SECRET"] = "secret string"
        self.app = create_application()
        self.app.testing = True
        with self.app.test_client() as c:
            response = c.post('/api_key', data='{"alias":"test", "secret": "secret string"}',
                              headers={"Content-Type": "application/json"})
            self.api_key = json.loads(response.data)["api_key"]

    def test_api_health(self):
        with self.app.test_client() as c:
            response = c.get('/health', query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)

    def test_no_api_key(self):
        with self.app.test_client() as c:
            response = c.get('/health')
            self.assertEqual(response.status_code, 401)

    def test_invalid_api_key(self):
        with self.app.test_client() as c:
            response = c.get('/health', query_string={"api_key": "invalid"})
            self.assertEqual(response.status_code, 403)
