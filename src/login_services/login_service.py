from src.model.user import User
from abc import abstractmethod

class LoginService:
    @abstractmethod
    def login(self, user: User) -> str:
        """
        Logins the user and generates a token valid for future actions

        :param user: the user to login
        :return: an string token for future authentication
        """

    @abstractmethod
    def get_email_by_token(self, login_token: str) -> str:
        """
        Gets the corresponding email fot a login token
            if the login token does not exists it returns a InvalidLoginToken exception

        :param login_token: the login token string
        :return: the email associated
        """