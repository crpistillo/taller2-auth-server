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

    @classmethod
    def factory(cls, name: str, *args, **kwargs) -> 'LoginService':
        """
        Factory pattern for login service

        :param name: the name of the login service to create in the factory
        :return: a login service object
        """
        types = {cls.__name__:cls for cls in LoginService.__subclasses__()}
        return types[name](*args, **kwargs)