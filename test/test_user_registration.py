from create_application import create_application
from src.model.user import User
from src.model.secured_password import SecuredPassword
import unittest
import json
from src.model.secured_password import SecuredPassword

class TestUserRegistration(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_application()
        self.app.testing = True

    def test_simple_register(self):
        with self.app.test_client() as c:
            response = c.post('/user', data='{"email":"giancafferata@hotmail.com", "fullname":"Gianmarco Cafferata", '
                                             '"phone_number":"11 1111-1111", "photo":"", "password":"asd123"}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 200)

    def test_simple_register_no_json(self):
        with self.app.test_client() as c:
            response = c.post('/user', data='')
            self.assertEqual(response.status_code, 400)

    def test_simple_missing_fields(self):
        with self.app.test_client() as c:
            response = c.post('/user', data='{"email":"giancafferata@hotmail.com", "fullname":"Gianmarco Cafferata", '
                                             '"phone_number":"11 1111-1111", "photo":""}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 400)

    def test_invalid_email_error(self):
        with self.app.test_client() as c:
            response = c.post('/user', data='{"email":"asd", "fullname":"Gianmarco Cafferata", '
                                             '"phone_number":"11 1111-1111", "photo":"", "password":"asd123"}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 400)

    def test_invalid_phone_number_error(self):
        with self.app.test_client() as c:
            response = c.post('/user', data='{"email":"giancafferata@hotmail.com", "fullname":"Gianmarco Cafferata", '
                                             '"phone_number":"asd", "photo":"", "password":"asd123"}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 400)

    def test_register_user_twice_error(self):
        with self.app.test_client() as c:
            response = c.post('/user', data='{"email":"giancafferata@hotmail.com", "fullname":"Gianmarco Cafferata", '
                                             '"phone_number":"11 1111-1111", "photo":"", "password":"asd123"}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 200)
            response = c.post('/user', data='{"email":"giancafferata@hotmail.com", "fullname":"Gianmarco", '
                                             '"phone_number":"11 2222-2222", "photo":"", "password":"asd1234"}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 400)

    def test_register_user_and_query(self):
        with self.app.test_client() as c:
            response = c.post('/user', data='{"email":"giancafferata@hotmail.com", "fullname":"Gianmarco Cafferata", '
                                             '"phone_number":"11 1111-1111", "photo":"", "password":"asd123"}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 200)

            response = c.post('/user/login', data='{"email":"giancafferata@hotmail.com", "password":"asd123"}',
                              headers={"Content-Type": "application/json"})
            token = json.loads(response.data)["login_token"]

            response = c.get('/user', query_string={"email": "giancafferata@hotmail.com"},
                       headers = {"Authorization": "Bearer %s" % token})
            self.assertEqual(response.status_code, 200)
            response_json = json.loads(response.data)
            self.assertEqual(response_json["email"], "giancafferata@hotmail.com")
            self.assertEqual(response_json["fullname"], "Gianmarco Cafferata")
            self.assertEqual(response_json["phone_number"], "11 1111-1111")
            self.assertEqual(response_json["photo"], "")
            secured_password = SecuredPassword.from_raw_password("asd123")
            self.assertEqual(response_json["password"], secured_password.serialize())
