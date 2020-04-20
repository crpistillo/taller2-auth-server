from typing import NoReturn
from src.model.user import User
from abc import abstractmethod
from src.model.user_token import UserToken

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
    def save_user_token(self, user_token: UserToken):
        """
        Saves an user_token
            ...
        """
