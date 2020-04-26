import logging
from typing import NoReturn
from src.model.user_recovery_token import UserRecoveryToken
from src.model.user import User

class EmailService:
    """
    Model entity for sending an email
    """
    logger = logging.getLogger(__name__)

    def __init__(self):
        pass

    def send_recovery_email(self, user: User, user_token: UserRecoveryToken) -> NoReturn:
        """

        :param user: The user who will receive the email
        :param user_token: The token to be sent
        """











