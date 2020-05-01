from typing import NoReturn
from src.model.user import User
from abc import abstractmethod
from src.model.user_recovery_token import UserRecoveryToken

class Database:
    """
    Database abstraction
    """

    @abstractmethod
    def save_user(self, user: User) -> NoReturn:
        """
        Saves an user
            if the user exists in the database it updates its fields
            if the user does not exist it creates it with the corresponding fields

        :param user: the user to save
        """

    @abstractmethod
    def search_user(self, email: str) -> User:
        """
        Searches an user by its email
            if the user exists it returns a User
            if the user does not exist it raises a UserNotFoundError

        :param email: the email to search the user
        :return: an User object
        """

    @abstractmethod
    def save_user_recovery_token(self, user_recovery_token: UserRecoveryToken) -> NoReturn:
        """
        Saves an user recovery token

        :param user_token: the user token to save
        """

    @abstractmethod
    def search_user_recovery_token(self, email: str) -> UserRecoveryToken:
        """
        Searches an user_recovery_token by its email
            if the user_recovery_token exists it returns a UserRecoveryToken
            if the token does not exist it raises a UserRecoveryTokenNotFoundError

        :param email: the email to search the user
        :return: an UserRecoveryToken object
        """

    @abstractmethod
    def login(self, user: User) -> str:
        """
        Logins the user and generates a token valid for future actions

        :param user: the user to login
        :return: an string token for future authentication
        """

    @abstractmethod
    def get_user_by_token(self, login_token: str) -> User:
        """
        Gets the corresponding user fot a login token
            if the login token does not exists it returns a InvalidLoginToken exception

        :param login_token: the login token string
        :return: the user associated
        """

    @classmethod
    def delete_user(self, email: str) -> NoReturn:
        """
        Removes all user data from database

        :param email: the email of the user to be deleted
        """

    @classmethod
    def factory(cls, name: str, *args, **kwargs) -> 'Database':
        """
        Factory pattern for database

        :param name: the name of the database to create in the factory
        :return: a database object
        """
        database_types = {cls.__name__:cls for cls in Database.__subclasses__()}
        return database_types[name](*args, **kwargs)