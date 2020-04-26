from create_application import create_application
import unittest

class TestFlaskDummy(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_application()
        self.app.testing = True

    def test_api_health(self):
        with self.app.test_client() as c:
            response = c.get('/health')
            self.assertEqual(response.status_code, 200)

    def test_get_not_allowed(self):
        # TODO: fill with all endpoints that are just POST
        with self.app.test_client() as c:
            response = c.get('/users/profile_query')
            self.assertEqual(response.status_code, 405)
            response = c.get('/users/register')
            self.assertEqual(response.status_code, 405)
