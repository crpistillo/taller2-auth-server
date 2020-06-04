from create_application import create_application
from src.model.user import User
from src.model.secured_password import SecuredPassword
import unittest
import json
import os

class TestApiKeyRegister(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["API_GENERATOR_SECRET"] = "secret string"
        self.app, self.controller = create_application(return_controller=True)
        self.app.testing = True

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
