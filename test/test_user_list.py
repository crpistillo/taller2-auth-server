from create_application import create_application
from src.model.user import User
from src.model.secured_password import SecuredPassword
import unittest
import json
import os

class TestUserList(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["API_GENERATOR_SECRET"] = "secret string"
        self.app = create_application()
        self.app.testing = True
        self.app, self.controller = create_application(return_controller=True)
        admin_user = User(email="admin@admin.com", fullname="Admin",
                          phone_number="11 1111-1111", photo="",
                          secured_password=SecuredPassword.from_raw_password("admin"),
                          admin=True)
        self.controller.database.save_user(admin_user)
        self.app.testing = True
        with self.app.test_client() as c:
            response = c.post('/api_key', data='{"alias":"test", "secret": "secret string"}',
                              headers={"Content-Type": "application/json"})
            self.api_key = json.loads(response.data)["api_key"]
            response = c.post('/user/login', data='{"email":"admin@admin.com", "password":"admin"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.admin_token = json.loads(response.data)["login_token"]

    def test_list_unauthorized_if_no_authentication(self):
        with self.app.test_client() as c:
            response = c.post('/user', data='{"email":"gcafferata@fi.uba.ar", "fullname":"Gianmarco Cafferata", '
                                             '"phone_number":"11 1111-1111", "photo":"", "password":"asd123"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            response = c.get('/registered_users', query_string={"users_per_page": 1, "page": 0,
                                                                "api_key": self.api_key})
            self.assertEqual(response.status_code, 401)

    def test_list_forbidden_if_not_admin(self):
        with self.app.test_client() as c:
            response = c.post('/user', data='{"email":"gcafferata@fi.uba.ar", "fullname":"Gianmarco Cafferata", '
                                             '"phone_number":"11 1111-1111", "photo":"", "password":"asd123"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            response = c.post('/user/login', data='{"email":"gcafferata@fi.uba.ar", "password":"asd123"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            token = json.loads(response.data)["login_token"]
            response = c.get('/registered_users', query_string={"users_per_page": 1, "page": 0,
                                                                "api_key": self.api_key},
                             headers = {"Authorization": "Bearer %s" % token})
            self.assertEqual(response.status_code, 403)

    def test_list_one_user(self):
        with self.app.test_client() as c:
            response = c.post('/user', data='{"email":"gcafferata@fi.uba.ar", "fullname":"Gianmarco Cafferata", '
                                             '"phone_number":"11 1111-1111", "photo":"", "password":"asd123"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            response = c.get('/registered_users', query_string={"users_per_page": 1, "page": 0,
                                                                "api_key": self.api_key},
                             headers = {"Authorization": "Bearer %s" % self.admin_token})
            self.assertEqual(response.status_code, 200)

    def test_list_missing_fields_error(self):
        with self.app.test_client() as c:
            response = c.get('/registered_users', query_string={"users_per_page": 4,
                                                                "api_key": self.api_key},
                             headers = {"Authorization": "Bearer %s" % self.admin_token})
            self.assertEqual(response.status_code, 400)
            response = c.get('/registered_users', query_string={"page": 1,
                                                                "api_key": self.api_key},
                             headers = {"Authorization": "Bearer %s" % self.admin_token})
            self.assertEqual(response.status_code, 400)

    def test_list_for_no_more_users_error(self):
        with self.app.test_client() as c:
            response = c.post('/user', data='{"email":"gcafferata@fi.uba.ar", "fullname":"Gianmarco Cafferata", '
                                            '"phone_number":"11 1111-1111", "photo":"", "password":"asd123"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            response = c.post('/user', data='{"email":"cpistillo@fi.uba.ar", "fullname":"Carolina Pistillo", '
                                            '"phone_number":"11 2222-2222", "photo":"", "password":"carolina"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            response = c.get('/registered_users', query_string={"users_per_page": 2, "page": 2,
                                                                "api_key": self.api_key},
                             headers = {"Authorization": "Bearer %s" % self.admin_token})
            self.assertEqual(response.status_code, 400)

    def test_list_ordered_by_email_and_paginated(self):
        with self.app.test_client() as c:
            response = c.post('/user', data='{"email":"m@fi.uba.ar", "fullname":"Martha Nielsen", '
                                            '"phone_number":"11 1111-1111", "photo":"", "password":"mn123"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            response = c.post('/user', data='{"email":"a@fi.uba.ar", "fullname":"Adam Kahnwald", '
                                            '"phone_number":"11 1111-1111", "photo":"", "password":"ak123"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            response = c.post('/user', data='{"email":"f@fi.uba.ar", "fullname":"Franciska Dopler", '
                                            '"phone_number":"11 1111-1111", "photo":"", "password":"fd123"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            response = c.post('/user', data='{"email":"u@fi.uba.ar", "fullname":"Ullrich Nielsen", '
                                            '"phone_number":"11 1111-1111", "photo":"", "password":"un123"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            response = c.get('/registered_users', query_string={"users_per_page": 3, "page": 0,
                                                                "api_key": self.api_key},
                             headers = {"Authorization": "Bearer %s" % self.admin_token})
            self.assertEqual(response.status_code, 200)
            response_json = json.loads(response.data)
            self.assertEqual(response_json["pages"], 2)
            self.assertEqual(response_json["results"][0]["email"], "a@fi.uba.ar")
            self.assertEqual(response_json["results"][1]["email"], "admin@admin.com")
            self.assertEqual(response_json["results"][2]["email"], "f@fi.uba.ar")
            response = c.get('/registered_users', query_string={"users_per_page": 3, "page": 1,
                                                                "api_key": self.api_key},
                             headers = {"Authorization": "Bearer %s" % self.admin_token})
            self.assertEqual(response.status_code, 200)
            response_json = json.loads(response.data)
            self.assertEqual(response_json["results"][0]["email"], "m@fi.uba.ar")
            self.assertEqual(response_json["results"][1]["email"], "u@fi.uba.ar")
            self.assertEqual(response_json["pages"], 2)








