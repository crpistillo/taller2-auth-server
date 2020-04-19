from typing import NoReturn, Dict
from src.model.user import User
from .database import Database
from .serialized.serialized_user import SerializedUser
from .exceptions.user_not_found_error import UserNotFoundError
from src.model.secured_password import SecuredPassword
import logging

class RamDatabase(Database):
    """
    Ram implementation of Database abstraction
    """
    serialized_users: Dict[str, SerializedUser]
    logger = logging.getLogger(__name__)
    def __init__(self):
        self.serialized_users = {}

    def save_user(self, user: User) -> NoReturn:
        """
        Saves an user
            if the user exists in the database it uploads its fields
            if the user does not exist it creates it with the corresponding fields

        :param user: the user to save
        """
        serialized_user = SerializedUser.from_user(user)
        self.logger.debug("Saving user with email %s" % serialized_user.email)
        self.serialized_users[serialized_user.email] = serialized_user

    def search_user(self, email: str) -> User:
        """
        Searches an user by its email
            if the user exists it returns a User
            if the user does not exist it raises a UserNotFoundError

        :param email: the email to search the user
        :return: an User object
        """
        if email not in self.serialized_users:
            raise UserNotFoundError
        self.logger.debug("Loading user with email %s" % email)
        serialized_user = self.serialized_users[email]
        secured_password = SecuredPassword(serialized_user.password)
        return User(email=serialized_user.email, fullname=serialized_user.fullname,
                    phone_number=serialized_user.phone_number, photo=serialized_user.photo,
                    secured_password=secured_password)