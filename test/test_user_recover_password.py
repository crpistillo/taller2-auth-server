from create_application import create_application
from src.model.user import User
from src.model.secured_password import SecuredPassword
import unittest
import json
from unittest import mock
from src.model.photo import Photo
import os

class TestUserRecoverPassword(unittest.TestCase):
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
            response = c.post('/user', data='{"email":"giancafferata@hotmail.com", "fullname":"Gianmarco Cafferata", '
                                             '"phone_number":"11 1111-1111", "photo":"", "password":"asd123"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            response = c.post('/user',
                              data='{"email":"cpistillo@fi.uba.ar", "fullname":"Carolina Pistillo", '
                                   '"phone_number":"11 1111-1111", "photo":"", "password":"carolina"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            response = c.post('/user/login', data='{"email":"admin@admin.com", "password":"admin"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.admin_token = json.loads(response.data)["login_token"]

    def test_recover_password_no_json(self):
        with self.app.test_client() as c:
            response = c.post('/user/recover_password', data='', query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 400)

    def test_recover_password_for_non_existing_user_error(self):
        with self.app.test_client() as c:
            response = c.post('/user/recover_password', data='{"email":"asd@fi.uba.ar"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 404)

    def test_recover_password_no_mandatory_fields(self):
        with self.app.test_client() as c:
            response = c.post('/user/recover_password', data='{"fullname": "Carolina Pistillo"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 400)

    @mock.patch('src.services.email.EmailService.send_recovery_email')
    def test_simple_recover_password(self, mock_send_recovery_email):
        with self.app.test_client() as c:
            response = c.post('/user/recover_password', data='{"email":"giancafferata@hotmail.com"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            mock_send_recovery_email.assert_called()
            args = mock_send_recovery_email.call_args_list
            self.assertEqual(len(args), 1)
            token = args[0][0][1].get_token()
            response = c.post('/user/new_password', data='{"email":"giancafferata@hotmail.com", "token": "%s",'
                                                         '"new_password": "asd1234"}' % token,
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            response = c.post('/user/login', data='{"email":"giancafferata@hotmail.com", "password": "asd123"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 403)
            response = c.post('/user/login', data='{"email":"giancafferata@hotmail.com", "password": "asd1234"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)

    @mock.patch('src.services.email.EmailService.send_recovery_email')
    def test_user_recover_password_and_delete_non_existing_user_error(self, mock_send_recovery_email):
        with self.app.test_client() as c:
            response = c.post('/user/recover_password', data='{"email":"giancafferata@hotmail.com"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            mock_send_recovery_email.assert_called()
            args = mock_send_recovery_email.call_args_list
            self.assertEqual(len(args), 1)
            token = args[0][0][1].get_token()
            response = c.post('/user/new_password', data='{"email":"giancafferata@hotmail.com", "token": "%s",'
                                                         '"new_password": "asd1234"}' % token,
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            response = c.delete('/user', query_string={"email": "giancafferata@hotmail.com", "api_key": self.api_key},
                                headers={"Authorization": "Bearer %s" % self.admin_token})
            self.assertEqual(response.status_code, 200)
            response = c.post('/user/recover_password', data='{"email":"giancafferata@hotmail.com"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 404)


    @mock.patch('src.services.email.EmailService.send_recovery_email')
    def test_recover_password_invalid_token(self, mock_send_recovery_email):
        with self.app.test_client() as c:
            response = c.post('/user/recover_password', data='{"email":"giancafferata@hotmail.com"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            mock_send_recovery_email.assert_called()
            args = mock_send_recovery_email.call_args_list
            self.assertEqual(len(args), 1)
            token = args[0][0][1].get_token()
            response = c.post('/user/new_password', data='{"email":"giancafferata@hotmail.com", "token": "asd",'
                                                         '"new_password": "asd1234"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 400)
            response = c.post('/user/login', data='{"email":"giancafferata@hotmail.com", "password": "asd1234"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 403)

    @mock.patch('src.services.email.EmailService.send_recovery_email')
    def test_recover_password_inexistent_token(self, mock_send_recovery_email):
        with self.app.test_client() as c:
            response = c.post('/user/new_password', data='{"email":"giancafferata@hotmail.com", "token": "asd",'
                                                         '"new_password": "asd1234"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 400)
            response = c.post('/user/login', data='{"email":"giancafferata@hotmail.com", "password": "asd1234"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 403)

    @mock.patch('src.services.email.EmailService.send_recovery_email')
    def test_recover_password_token_for_other_user(self, mock_send_recovery_email):
        with self.app.test_client() as c:
            response = c.post('/user/recover_password', data='{"email":"cpistillo@fi.uba.ar"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            mock_send_recovery_email.assert_called()
            args = mock_send_recovery_email.call_args_list
            self.assertEqual(len(args), 1)
            token = args[0][0][1].get_token()
            response = c.post('/user/new_password', data='{"email":"giancafferata@hotmail.com", "token": "asd",'
                                                         '"new_password": "asd1234"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 400)
            response = c.post('/user/login', data='{"email":"giancafferata@hotmail.com", "password": "asd1234"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 403)

    @mock.patch('src.services.email.EmailService.send_recovery_email')
    def test_new_password_user_not_found(self, mock_send_recovery_email):
        with self.app.test_client() as c:
            response = c.post('/user/new_password', data='{"email":"asd@fi.uba.ar", "token": "asd",'
                                                         '"new_password": "asd1234"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 404)

    @mock.patch('src.services.email.EmailService.send_recovery_email')
    def test_new_password_no_json(self, mock_send_recovery_email):
        with self.app.test_client() as c:
            response = c.post('/user/new_password', data='', query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 400)

    def test_new_password_no_mandatory_fields(self):
        with self.app.test_client() as c:
            response = c.post('/user/new_password', data='{"fullname": "Carolina Pistillo"}',
                              headers={"Content-Type": "application/json"},
                              query_string={"api_key": self.api_key})
            self.assertEqual(response.status_code, 400)

