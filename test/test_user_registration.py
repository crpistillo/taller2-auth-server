from create_application import create_application
import unittest
import json

class TestUserRegistration(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_application()
        self.app.testing = True

    def test_querying_for_non_existing_user_error(self):
        with self.app.test_client() as c:
            response = c.get('/user', query_string={"email": "giancafferata@hotmail.com"})
            self.assertEqual(response.status_code, 404)

    def test_querying_user_without_email(self):
        with self.app.test_client() as c:
            response = c.get('/user', query_string={})
            self.assertEqual(response.status_code, 400)

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
        # TODO: Query for all fields
        with self.app.test_client() as c:
            response = c.post('/user', data='{"email":"giancafferata@hotmail.com", "fullname":"Gianmarco Cafferata", '
                                             '"phone_number":"11 1111-1111", "photo":"", "password":"asd123"}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 200)
            response = c.get('/user', query_string={"email": "giancafferata@hotmail.com"})
            self.assertEqual(response.status_code, 200)
            response_json = json.loads(response.data)
            self.assertEqual(response_json["email"], "giancafferata@hotmail.com")
            self.assertEqual(response_json["fullname"], "Gianmarco Cafferata")
            self.assertEqual(response_json["phone_number"], "11 1111-1111")

    def test_query_for_inexistent_user(self):
        # TODO: Query for all fields
        with self.app.test_client() as c:
            response = c.post('/user', data='{"email":"giancafferata@hotmail.com", "fullname":"Gianmarco Cafferata", '
                                             '"phone_number":"11 1111-1111", "photo":"", "password":"asd123"}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 200)
            response = c.get('/user', query_string={"email": "jian01.cs@gmail.com"})
            self.assertEqual(response.status_code, 404)
