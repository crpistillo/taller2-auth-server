from create_application import create_application
import unittest

class TestUserRecoverPassword(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_application()
        self.app.testing = True

    def test_recover_password_no_json(self):
        with self.app.test_client() as c:
            response = c.post('/user/recover_password', data='')
            self.assertEqual(response.status_code, 400)

    def test_recover_password_for_non_existing_user_error(self):
        with self.app.test_client() as c:
            response = c.post('/user/recover_password', data='{"email":"cpistillo@fi.uba.ar"}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 404)
