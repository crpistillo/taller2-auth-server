from create_application import create_application
from src.model.user import User
from src.model.secured_password import SecuredPassword
import unittest
import json

class TestUserQuery(unittest.TestCase):
    def setUp(self) -> None:
        self.app, self.controller = create_application(return_controller=True)
        admin_user = User(email="admin@admin.com", fullname="Admin",
                          phone_number="11 1111-1111", photo="",
                          secured_password=SecuredPassword.from_raw_password("admin"),
                          admin=True)
        self.controller.database.save_user(admin_user)
        self.app.testing = True

    def test_querying_unathorized_error(self):
        with self.app.test_client() as c:
            response = c.get('/user', query_string={"email": "giancafferata@hotmail.com"})
            self.assertEqual(response.status_code, 401)

    def test_querying_for_non_existing_user_error(self):
        with self.app.test_client() as c:
            response = c.post('/user/login', data='{"email":"admin@admin.com", "password":"admin"}',
                              headers={"Content-Type": "application/json"})
            token = json.loads(response.data)["login_token"]
            response = c.get('/user', query_string={"email": "giancafferata@hotmail.com"},
                             headers={"Authorization": "Bearer %s" % token})
            self.assertEqual(response.status_code, 404)

    def test_querying_user_without_email(self):
        with self.app.test_client() as c:
            response = c.post('/user/login', data='{"email":"admin@admin.com", "password":"admin"}',
                              headers={"Content-Type": "application/json"})
            token = json.loads(response.data)["login_token"]
            response = c.get('/user', query_string={},
                             headers={"Authorization": "Bearer %s" % token})
            self.assertEqual(response.status_code, 400)

    def test_query_for_inexistent_user_after_registering_valid(self):
        with self.app.test_client() as c:
            response = c.post('/user', data='{"email":"giancafferata@hotmail.com", "fullname":"Gianmarco Cafferata", '
                                             '"phone_number":"11 1111-1111", "photo":"", "password":"asd123"}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 200)
            response = c.post('/user/login', data='{"email":"admin@admin.com", "password":"admin"}',
                              headers={"Content-Type": "application/json"})
            token = json.loads(response.data)["login_token"]

            response = c.get('/user', query_string={"email": "jian01.cs@gmail.com"},
                             headers={"Authorization": "Bearer %s" % token})
            self.assertEqual(response.status_code, 404)

    def test_query_for_other_not_allowed_error(self):
        with self.app.test_client() as c:
            response = c.post('/user', data='{"email":"giancafferata@hotmail.com", "fullname":"Gianmarco Cafferata", '
                                             '"phone_number":"11 1111-1111", "photo":"", "password":"asd123"}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 200)
            response = c.post('/user', data='{"email":"gcafferata@fi.uba.ar", "fullname":"Gianmarco Cafferata", '
                                             '"phone_number":"11 1111-1111", "photo":"", "password":"asd123"}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 200)
            response = c.post('/user/login', data='{"email":"gcafferata@fi.uba.ar", "password":"asd123"}',
                              headers={"Content-Type": "application/json"})
            token = json.loads(response.data)["login_token"]

            response = c.get('/user', query_string={"email": "giancafferata@hotmail.com"},
                             headers={"Authorization": "Bearer %s" % token})
            self.assertEqual(response.status_code, 403)