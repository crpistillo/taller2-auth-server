from create_application import create_application
import unittest
import json
import os

class TestUserLogin(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["API_GENERATOR_SECRET"] = "secret string"
        self.app = create_application()
        self.app.testing = True
        with self.app.test_client() as c:
            response = c.post('/api_key', data='{"alias":"test", "secret": "secret string"}',
                              headers={"Content-Type": "application/json"})
            self.api_key = json.loads(response.data)["api_key"]

    def test_login_no_json(self):
        with self.app.test_client() as c:
            response = c.post('/user/login', data='', query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 400)

    def test_login_missing_fields(self):
        with self.app.test_client() as c:
            response = c.post('/user/login', data='{"email":"cpistillo@fi.uba.ar"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 400)

    def test_login_for_non_existing_user_error(self):
        with self.app.test_client() as c:
            response = c.post('/user/login', data='{"email":"cpistillo@fi.uba.ar", "password": "carolina" }',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 404)

    def test_register_user_and_login(self):
        with self.app.test_client() as c:
            response = c.post('/user',
                              data={"email":"cpistillo@fi.uba.ar", "fullname":"Carolina Pistillo",
                                   "phone_number":"11 1111-1111", "password":"carolina"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            response = c.post('/user/login', data='{"email":"cpistillo@fi.uba.ar", "password": "carolina" }',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.data)["user"]["email"], "cpistillo@fi.uba.ar")

    def test_login_for_wrong_credentials_error(self):
        with self.app.test_client() as c:
            response = c.post('/user',
                              data={"email":"cpistillo@fi.uba.ar", "fullname":"Carolina Pistillo",
                                   "phone_number":"11 1111-1111", "password":"carolina"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            response = c.post('/user/login', data='{"email":"cpistillo@fi.uba.ar", "password": "caro" }',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 403)

    def test_register_user_and_login_for_non_existing_user_error(self):
        with self.app.test_client() as c:
            response = c.post('/user',
                              data={"email":"cpistillo@fi.uba.ar", "fullname":"Carolina Pistillo",
                                   "phone_number":"11 1111-1111", "password":"carolina"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            response = c.post('/user/login', data='{"email":"pistillo@fi.uba.ar", "password": "carolina" }',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 404)

    def test_user_login_query(self):
        with self.app.test_client() as c:
            response = c.post('/user',
                              data={"email":"cpistillo@fi.uba.ar", "fullname":"Carolina Pistillo",
                                   "phone_number":"11 1111-1111", "password":"carolina"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            response = c.post('/user/login', data='{"email":"cpistillo@fi.uba.ar", "password": "carolina" }',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.data)["user"]["email"], "cpistillo@fi.uba.ar")
            login_token = json.loads(response.data)["login_token"]
            response = c.get('/user/login', headers={"Authorization": "Bearer %s" % login_token},
                             query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.data)["email"], "cpistillo@fi.uba.ar")

