import logging
from typing import NoReturn
from src.model.user_recovery_token import UserRecoveryToken
from src.model.user import User
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *
import os

class EmailService:
    """
    Model entity for sending an email
    """
    logger = logging.getLogger(__name__)

    def __init__(self, sendgrid_email_env_name: str, sendgrid_api_key_env_name: str):
        """
        Creates an email service based on sendgrid

        :param sendgrid_email_env_name: the env variable where the email is
        :param sendgrid_api_key_env_name: the env variable where the api key is
        """
        try:
            self.sendgrid_email = os.environ[sendgrid_email_env_name]
            self.sendgrid_api_key = os.environ[sendgrid_api_key_env_name]
        except KeyError:
            self.sendgrid_email = None
            self.sendgrid_api_key = None
            self.logger.error("Failed to initialize email service")
            return
        self.logger.info("Email service initialized")

    def send_recovery_email(self, user: User, user_token: UserRecoveryToken) -> NoReturn:
        """
        Sends the recovery token to the user
            if it fails does nothing

        :param user: The user who will receive the email
        :param user_token: The token to be sent
        """
        if not self.sendgrid_email or not self.sendgrid_api_key:
            self.logger.error("Failed to send recovery token to %s" % user.get_email())
            return
        from_email = Email(self.sendgrid_email)
        to_email = To(user.get_email())
        subject = "Chotuve password recovery token"
        content = Content("text/plain", "Recovery token: %s" % user_token.get_token())
        mail = Mail(from_email, to_email, subject, content)
        sg = SendGridAPIClient(self.sendgrid_api_key)
        try:
            response = sg.client.mail.send.post(request_body=mail.get())
            response.raise_for_status()
            self.logger.debug("Sent recovery token to %s" % user.get_email())
        except Exception:
            self.logger.exception("Failed to send recovery token to %s" % user.get_email())
            return
