from create_application import create_application
import unittest

class TestFlaskDummy(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_application()
        self.app.testing = True

    def test_querying_for_non_existing_user_error(self):
        # TODO: query for other fields when thats implemented
        with self.app.test_client() as c:
            response = c.post('/users/query/phone_number', data='{"email":"giancafferata@hotmail.com"}',
                              headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 400)
