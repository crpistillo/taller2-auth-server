from create_application import create_application
from src.model.user import User
from src.model.secured_password import SecuredPassword
from src.model.photo import Photo
import unittest
import json
import os

class TestUserDelete(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["API_GENERATOR_SECRET"] = "secret string"
        self.app, self.controller = create_application(return_controller=True)
        admin_user = User(email="admin@admin.com", fullname="Admin",
                          phone_number="11 1111-1111", photo=Photo(),
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

    def test_user_delete_without_authorization(self):
        with self.app.test_client() as c:
            response = c.delete('/user', query_string={"fullname": "Carolina", "api_key": self.api_key})
            self.assertEqual(response.status_code, 401)

    def test_user_delete_for_missing_fields_error(self):
        with self.app.test_client() as c:
            response = c.delete('/user', query_string={"fullname": "Carolina", "api_key": self.api_key},
                                headers={"Authorization": "Bearer %s" % self.admin_token})
            self.assertEqual(response.status_code, 400)

    def test_user_delete_for_non_existing_user_error(self):
        with self.app.test_client() as c:
            response = c.delete('/user', query_string={"email": "caropistillo@gmail.com", "api_key": self.api_key},
                                headers={"Authorization": "Bearer %s" % self.admin_token})
            self.assertEqual(response.status_code, 404)

    def test_user_delete_success(self):
        with self.app.test_client() as c:
            response = c.post('/user', data={"email":"caropistillo@gmail.com", "password": "carolina15", "fullname":
                                 "Carolina Rocio", "phone_number":"11 1111-1111"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            response = c.delete('/user', query_string={"email": "caropistillo@gmail.com", "api_key": self.api_key},
                                headers={"Authorization": "Bearer %s" % self.admin_token})
            self.assertEqual(response.status_code, 200)

    def test_user_delete_myself_success(self):
        with self.app.test_client() as c:
            response = c.post('/user', data={"email":"caropistillo@gmail.com", "password": "carolina15", "fullname":
                                 "Carolina Rocio", "phone_number":"11 1111-1111"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)

            response = c.post('/user/login', data='{"email":"caropistillo@gmail.com", "password":"carolina15"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            my_token = json.loads(response.data)["login_token"]

            response = c.delete('/user', query_string={"email": "caropistillo@gmail.com", "api_key": self.api_key},
                                headers={"Authorization": "Bearer %s" % my_token})
            self.assertEqual(response.status_code, 200)

    def test_user_delete_and_login_non_existing_user_error(self):
        with self.app.test_client() as c:
            response = c.post('/user', data={"email":"caropistillo@gmail.com", "password": "carolina15", "fullname":
                            "Carolina Rocio", "phone_number":"11 1111-1111"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            response = c.delete('/user', query_string={"email": "caropistillo@gmail.com", "api_key": self.api_key},
                                headers={"Authorization": "Bearer %s" % self.admin_token})
            self.assertEqual(response.status_code, 200)
            response = c.post('/user/login', data='{"email":"caropistillo@gmail.com", "password": "carolina15" }',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 404)

    def test_user_delete_and_query_non_existing_user_error(self):
        with self.app.test_client() as c:
            response = c.post('/user', data={"email":"caropistillo@gmail.com", "password": "carolina15", "fullname":
                                 "Carolina Rocio", "phone_number":"11 1111-1111"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            response = c.delete('/user', query_string={"email": "caropistillo@gmail.com", "api_key": self.api_key},
                                headers={"Authorization": "Bearer %s" % self.admin_token})
            self.assertEqual(response.status_code, 200)

            response = c.get('/user', query_string={"email": "caropistillo@gmail.com", "api_key": self.api_key},
                             headers={"Authorization": "Bearer %s" % self.admin_token})
            self.assertEqual(response.status_code, 404)

    def test_user_delete_and_update_non_existing_user_error(self):
        with self.app.test_client() as c:
            response = c.post('/user', data={"email":"caropistillo@gmail.com", "password": "carolina15", "fullname":
                                 "Carolina Rocio", "phone_number":"11 1111-1111"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            response = c.delete('/user', query_string={"email": "caropistillo@gmail.com", "api_key": self.api_key},
                                headers={"Authorization": "Bearer %s" % self.admin_token})
            self.assertEqual(response.status_code, 200)
            response = c.put('/user', query_string={"email": "caropistillo@gmail.com", "api_key": self.api_key},
                             data='{"fullname":"Carolina Pistillo", "phone_number":"11 3263-7625", '
                                  '"password":"carolina"}', headers={"Content-Type": "application/json",
                                                                     "Authorization": "Bearer %s" % self.admin_token})
            self.assertEqual(response.status_code, 404)

    def test_delete_for_other_not_allowed_error(self):
        with self.app.test_client() as c:
            response = c.post('/user', data={"email":"giancafferata@hotmail.com", "fullname":"Gianmarco Cafferata",
                                            "phone_number":"11 1111-1111", "password":"asd123"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            response = c.post('/user', data={"email":"gcafferata@fi.uba.ar", "fullname":"Gianmarco Cafferata",
                                            "phone_number":"11 1111-1111", "password":"asd123"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            response = c.post('/user/login', data='{"email":"gcafferata@fi.uba.ar", "password":"asd123"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            token = json.loads(response.data)["login_token"]

            response = c.delete('/user', query_string={"email": "giancafferata@hotmail.com", "api_key": self.api_key},
                             headers={"Authorization": "Bearer %s" % token})
            self.assertEqual(response.status_code, 403)


