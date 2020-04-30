import jwt
import datetime
from src.model.user import User

class UserRecoveryToken:
    """
    Model entity for the user_token
    """
    email: str
    token: str
    timestamp: str

    def __init__(self, email: str, token: str, timestamp: str):
        """
        UserToken initializer

        :param email: the email of the user
        :param token: the token given when logged in
        :param timestamp: the date and time when logged in
        """
        self.email = email
        self.token = token
        self.timestamp = timestamp

    @classmethod
    def from_user(cls, user: User, recovery_secret_key: str) -> 'UserRecoveryToken':
        """
        Generates a Base64 string encoded for web application
        :param user: the user for the recovery token
        :param recovery_secret_key: a recovery secret key to generate the token
        :return: a UserToken
        """
        timestamp = datetime.datetime.now().isoformat()
        payload = {
            "user_email": user.get_email(),
            "timestamp": timestamp
        }
        generated_token = jwt.encode(payload, recovery_secret_key, algorithm='HS256').decode("utf-8")
        return cls(user.get_email(), generated_token, timestamp)

    def get_token(self):
        return self.token

    def get_email(self):
        return self.email

    def token_match(self, other: str) -> bool:
        """
        Responsible for comparing to token

        :param other: other token
        :return: a boolean indicating if the tokens are equal
        """
        return other == self.token


