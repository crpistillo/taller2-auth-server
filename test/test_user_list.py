from create_application import create_application
from src.model.user import User
from src.model.secured_password import SecuredPassword
import unittest
import json

class TestUserList(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_application()
        self.app.testing = True

    # TODO: this is a dummy test, can be removed/replaced
    def test_list_one_user(self):
        with self.app.test_client() as c:
            response = c.post('/user', data='{"email":"gcafferata@fi.uba.ar", "fullname":"Gianmarco Cafferata", '
                                             '"phone_number":"11 1111-1111", "photo":"", "password":"asd123"}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 200)
            response = c.get('/registered_users', query_string={"users_per_page": 1, "page": 0})
            self.assertEqual(response.status_code, 200)
