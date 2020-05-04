from create_application import create_application
import unittest
import json

class TestUserList(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_application()
        self.app.testing = True

    def test_list_one_user(self):
        with self.app.test_client() as c:
            response = c.post('/user', data='{"email":"gcafferata@fi.uba.ar", "fullname":"Gianmarco Cafferata", '
                                             '"phone_number":"11 1111-1111", "photo":"", "password":"asd123"}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 200)
            response = c.get('/registered_users', query_string={"users_per_page": 1, "page": 0})
            self.assertEqual(response.status_code, 200)

    def test_list_missing_fields_error(self):
        with self.app.test_client() as c:
            response = c.get('/registered_users', query_string={"users_per_page": 4})
            self.assertEqual(response.status_code, 400)
            response = c.get('/registered_users', query_string={"page": 1})
            self.assertEqual(response.status_code, 400)

    def test_list_for_no_more_users_error(self):
        with self.app.test_client() as c:
            response = c.post('/user', data='{"email":"gcafferata@fi.uba.ar", "fullname":"Gianmarco Cafferata", '
                                            '"phone_number":"11 1111-1111", "photo":"", "password":"asd123"}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 200)
            response = c.post('/user', data='{"email":"cpistillo@fi.uba.ar", "fullname":"Carolina Pistillo", '
                                            '"phone_number":"11 2222-2222", "photo":"", "password":"carolina"}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 200)
            response = c.get('/registered_users', query_string={"users_per_page": 2, "page": 2})
            self.assertEqual(response.status_code, 400)

    def test_list_empty_list(self):
        with self.app.test_client() as c:
            response = c.get('/registered_users', query_string={"users_per_page": 1, "page": 0})
            self.assertEqual(response.status_code, 200)
            response_json = json.loads(response.data)
            self.assertEqual(response_json["pages"], 0)
            self.assertEqual(response_json["results"], [])

    def test_list_ordered_by_email_and_paginated(self):
        with self.app.test_client() as c:
            response = c.post('/user', data='{"email":"m@fi.uba.ar", "fullname":"Martha Nielsen", '
                                            '"phone_number":"11 1111-1111", "photo":"", "password":"mn123"}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 200)
            response = c.post('/user', data='{"email":"a@fi.uba.ar", "fullname":"Adam Kahnwald", '
                                            '"phone_number":"11 1111-1111", "photo":"", "password":"ak123"}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 200)
            response = c.post('/user', data='{"email":"f@fi.uba.ar", "fullname":"Franciska Dopler", '
                                            '"phone_number":"11 1111-1111", "photo":"", "password":"fd123"}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 200)
            response = c.post('/user', data='{"email":"u@fi.uba.ar", "fullname":"Ullrich Nielsen", '
                                            '"phone_number":"11 1111-1111", "photo":"", "password":"un123"}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 200)
            response = c.get('/registered_users', query_string={"users_per_page": 3, "page": 0})
            self.assertEqual(response.status_code, 200)
            response_json = json.loads(response.data)
            self.assertEqual(response_json["pages"], 2)
            self.assertEqual(response_json["results"][0]["email"], "a@fi.uba.ar")
            self.assertEqual(response_json["results"][1]["email"], "f@fi.uba.ar")
            self.assertEqual(response_json["results"][2]["email"], "m@fi.uba.ar")
            response = c.get('/registered_users', query_string={"users_per_page": 3, "page": 1})
            self.assertEqual(response.status_code, 200)
            response_json = json.loads(response.data)
            self.assertEqual(response_json["results"][0]["email"], "u@fi.uba.ar")
            self.assertEqual(response_json["pages"], 2)








