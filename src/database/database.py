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
            if the user exists in the database it uploads its fields
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
    def save_recovery_token(self, user_token: UserRecoveryToken) -> NoReturn:
        """
        Saves an user recovery token

        :param user_token: the user token to save
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