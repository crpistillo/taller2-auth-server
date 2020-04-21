import datetime
import jwt
import os

class UserToken:
    """
    Model entity for the user_token
    """
    email: str
    token: str
    date: str
    token_type: str

    def __init__(self, email: str, token: str, timestamp: str, token_type: str):
        """
        UserToken initializer

        :param email: the email of the user
        :param token: the token given when logged in
        :param timestamp: the date and time when logged in
        """
        self.email = email
        self.token = token
        self.timestamp = timestamp
        self.token_type = token_type

    @classmethod
    def generate_token(cls, email: str, token_type: str) -> 'UserToken':
        """
        Generates a Base64 string encoded for web application
        :param email: the email associated with the token
        :param token_type: the context under which the user receives the
                            token (login,password-recover,etc)
        :return: a UserToken
        """
        time = datetime.datetime.now().__str__()
        payload = {
            "user_email": email,
            "timestamp": time,
            "type": token_type
        }
        generated_token = jwt.encode(payload, 'secret', algorithm='HS256').decode("utf-8")
        return cls(email, generated_token, time, token_type)

    def get_token(self):
        return self.token


