from create_application import create_application
from src.model.user import User
from src.model.secured_password import SecuredPassword
import unittest
import json
import os
import requests
from unittest.mock import MagicMock

class FakeResponse:
    def __init__(self, status_code: int):
        self.status_code = status_code

    def json(self):
        return {}

    def raise_for_status(self):
        return

class TestApiKeyRegister(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["API_GENERATOR_SECRET"] = "secret string"
        self.app, self.controller = create_application(return_controller=True)
        self.app.testing = True
        self.get = requests.get

    def tearDown(self) -> None:
        requests.get = self.get

    def test_correct_api_key_new_call(self):
        with self.app.test_client() as c:
            response = c.post('/api_key', data='{"alias":"test", "secret": "secret string"}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 200)

    def test_correct_api_key_new_no_json(self):
        with self.app.test_client() as c:
            response = c.post('/api_key', data='{"alias":"test", "secret": "secret string"}')
            self.assertEqual(response.status_code, 400)

    def test_correct_api_key_new_mandatory_field(self):
        with self.app.test_client() as c:
            response = c.post('/api_key', data='{"alias":"test"}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 400)

    def test_correct_api_key_new_bad_secret(self):
        with self.app.test_client() as c:
            response = c.post('/api_key', data='{"alias":"test", "secret": "secret string 2"}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 403)

    def test_api_key_new_then_get_status(self):
        with self.app.test_client() as c:
            response = c.post('/api_key', data='{"alias":"test", "secret": "secret string",'
                                               '"health_endpoint": "http://google.com"}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 200)
            response = c.get('/app_servers')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0], {"server_alias": "test", "is_healthy": True})

    def test_api_key_status_unhealthy(self):
        with self.app.test_client() as c:
            response = c.post('/api_key', data='{"alias":"test", "secret": "secret string",'
                                               '"health_endpoint": "https://localhost:5555"}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 200)
            response = c.get('/app_servers')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0], {"server_alias": "test", "is_healthy": False})

