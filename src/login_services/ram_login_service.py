from src.model.user import User
from src.login_services.login_service import LoginService
import hashlib
from src.login_services.exceptions.invalid_login_token import InvalidLoginToken

class RamLoginService(LoginService):

    def __init__(self):
        self.tokens = {}

    def login(self, user: User) -> str:
        """
        Logins the user and generates a token valid for future actions

        :param user: the user to login
        :return: an string token for future authentication
        """
        token = hashlib.sha256(user.get_email().encode("utf-8")).hexdigest()
        self.tokens[token] = user.get_email()
        return token

    def get_email_by_token(self, login_token: str) -> str:
        """
        Gets the corresponding email fot a login token
            if the login token does not exists it returns a InvalidLoginToken exception

        :param login_token: the login token string
        :return: the email associated
        """
        if login_token not in self.tokens:
            raise InvalidLoginToken
        return self.tokens[login_token]