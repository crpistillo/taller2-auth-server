import datetime
import os
import jwt

class UserToken:
    """
    Model entity for the user_token
    """
    email: str
    token: str

    def __init__(self, email: str, token: str):
        """
        UserToken initializer

        :param email: the email of the user
        :param token: the token given when logged in
        """
        self.email = email
        self.token = token

    @classmethod
    def generate_token(cls, email: str) -> 'UserToken':
        """
        Generates a Base64 string encoded for web application
        :param email: the email associated with the token
        :return: a UserToken
        """
        payload = {
            "user_email": email,
            "timestamp": datetime.datetime.now().__str__()
        }

        return cls(email, "token")#cambiar por alguna funcion: discutir con gian: jwt?

    def get_token(self):
        return self.token


