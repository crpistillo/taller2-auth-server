from create_application import create_application
import unittest
import json
from src.model.secured_password import SecuredPassword

class TestUserRegistration(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_application()
        self.app.testing = True

    def test_user_update_no_json(self):
        with self.app.test_client() as c:
            response = c.put('/user', query_string={"email": "caropistillo@gmail.com"}, data='')
            self.assertEqual(response.status_code, 400)

    def test_user_update_for_missing_fields_error(self):
        with self.app.test_client() as c:
            response = c.put('/user', query_string={"fullname": "Carolina"})
            self.assertEqual(response.status_code, 400)

    def test_user_update_for_non_existing_user_error(self):
        with self.app.test_client() as c:
            response = c.put('/user', query_string={"email": "caropistillo@gmail.com"},
                             data='{"fullname":"Carolina Pistillo", "phone_number":"11 1111-1111", "photo":"", '
                                '"password":"carolina"}', headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 404)

    def test_user_update_success(self):
        with self.app.test_client() as c:
            response = c.post('/user', data='{"email":"caropistillo@gmail.com", "password": "carolina15", "fullname":'
                                 '"Carolina Rocio", "phone_number":"11 1111-1111", "photo":""}',
                                                        headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 200)
            response = c.put('/user', query_string={"email": "caropistillo@gmail.com"},
                             data='{"fullname":"Carolina Pistillo", "phone_number":"11 3263-7625", "photo":"caro.jpg", '
                                '"password":"carolina"}', headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 200)

    def test_user_update_and_query(self):
        with self.app.test_client() as c:
            response = c.post('/user', data='{"email":"caropistillo@gmail.com", "password": "carolina15", "fullname":'
                                 '"Carolina Rocio", "phone_number":"11 1111-1111", "photo":""}',
                                                        headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 200)
            response = c.put('/user', query_string={"email": "caropistillo@gmail.com"},
                             data='{"fullname":"Carolina Pistillo", "phone_number":"11 3263-7625", "photo":"caro.jpg", '
                                '"password":"carolina"}', headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 200)
            response = c.get('/user', query_string={"email": "caropistillo@gmail.com"})
            self.assertEqual(response.status_code, 200)
            response_json = json.loads(response.data)
            self.assertEqual(response_json["email"], "caropistillo@gmail.com")
            self.assertEqual(response_json["fullname"], "Carolina Pistillo")
            self.assertEqual(response_json["phone_number"], "11 3263-7625")
            self.assertEqual(response_json["photo"], "caro.jpg")
            secured_password = SecuredPassword.from_raw_password("carolina")
            self.assertEqual(response_json["password"], secured_password.serialize())

    def test_user_update_and_login(self):
        with self.app.test_client() as c:
            response = c.post('/user', data='{"email":"caropistillo@gmail.com", "password": "carolina15", "fullname":'
                                 '"Carolina Rocio", "phone_number":"11 1111-1111", "photo":""}',
                                                        headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 200)
            response = c.put('/user', query_string={"email": "caropistillo@gmail.com"},
                             data='{"fullname":"Carolina Pistillo", "phone_number":"11 3263-7625", "photo":"caro.jpg", '
                                '"password":"carolina"}', headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 200)
            response = c.post('/user/login', data='{"email":"caropistillo@gmail.com", "password": "carolina" }',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 200)


