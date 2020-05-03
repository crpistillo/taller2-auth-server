import unittest
from unittest import mock
from src.services.email import EmailService
from src.model.user import User
from src.model.user_recovery_token import UserRecoveryToken
from src.model.secured_password import SecuredPassword
import sendgrid
import os


class TestEmailService(unittest.TestCase):
    def setUp(self) -> None:
        secured_password = SecuredPassword.from_raw_password("password")
        self.test_user = User(email="giancafferata@hotmail.com", fullname="Gianmarco Cafferata",
                              phone_number="11 1111-1111", photo="", secured_password=secured_password)
        self.recovery_token = UserRecoveryToken.from_user(self.test_user, "dummy")

    @mock.patch('sendgrid.SendGridAPIClient.send')
    def test_send_recovery_token(self, mock_sendgrid_send):
        os.environ["SENDGRID_API_KEY"] = "dummy"
        os.environ["SENDGRID_EMAIL"] = "asd@asd.com"
        self.email_service = EmailService(sendgrid_api_key_env_name="SENDGRID_API_KEY",
                                          sendgrid_email_env_name="SENDGRID_EMAIL")
        self.email_service.send_recovery_email(self.test_user, self.recovery_token)
        mock_sendgrid_send.assert_called()
        args = mock_sendgrid_send.call_args_list
        self.assertEqual(len(args), 1)
        self.assertEqual(args[0][0][0].get()["from"]["email"], "asd@asd.com")

    @mock.patch('sendgrid.SendGridAPIClient.send')
    def test_invalid_envs_wont_send(self, mock_sendgrid_send):
        self.email_service = EmailService(sendgrid_api_key_env_name="NOT_SETTED_ENV_VARIABLE",
                                          sendgrid_email_env_name="NOT_SETTED_ENV_VARIABLE")
        self.email_service.send_recovery_email(self.test_user, self.recovery_token)
        mock_sendgrid_send.assert_not_called()

    @mock.patch('sendgrid.SendGridAPIClient.send')
    def test_exception(self, mock_sendgrid_send):
        os.environ["SENDGRID_API_KEY"] = "dummy"
        os.environ["SENDGRID_EMAIL"] = "asd@asd.com"
        mock_sendgrid_send.side_effect = Exception()
        self.email_service = EmailService(sendgrid_api_key_env_name="SENDGRID_API_KEY",
                                          sendgrid_email_env_name="SENDGRID_EMAIL")
        self.email_service.send_recovery_email(self.test_user, self.recovery_token)
        mock_sendgrid_send.assert_called()