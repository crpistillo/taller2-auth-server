from typing import NoReturn, Tuple
from src.model.user import User
from abc import abstractmethod
from src.model.user_recovery_token import UserRecoveryToken
from src.model.secured_password import SecuredPassword
from src.database.serialized.serialized_user import SerializedUser
from src.model.api_key import ApiKey
from typing import List, Optional, Dict
from src.model.photo import Photo
from datetime import datetime
from src.model.api_calls_statistics import ApiCallsStatistics

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

    @abstractmethod
    def delete_user(self, email: str) -> NoReturn:
        """
        Removes all user data from database

        :param email: the email of the user to be deleted
        """

    def update_user(self, user: User, password: Optional[SecuredPassword] = None,
                    fullname: Optional[str] = None,
                    phone_number: Optional[str] = None,
                    photo: Optional[Photo] = None) -> NoReturn:
        """
        Updates a user

        :param user: the user to update
        :param password: the password to update
        :param fullname: the full name to update
        :param phone_number: phone number to update
        :param photo: the photo to update
        """
        if password:
            user.set_password(password)
        if fullname:
            user.set_fullname(fullname)
        if phone_number:
            user.set_phone_number(phone_number)
        if photo:
            user.set_photo(photo)

        self.save_user(user)

    @classmethod
    def factory(cls, name: str, *args, **kwargs) -> 'Database':
        """
        Factory pattern for database

        :param name: the name of the database to create in the factory
        :return: a database object
        """
        database_types = {cls.__name__:cls for cls in Database.__subclasses__()}
        return database_types[name](*args, **kwargs)

    @abstractmethod
    def get_users(self, page: int, users_per_page: int) -> Tuple[List[SerializedUser], int]:
        """
        Get a list of users paginated
            if there are no more pages returns a NoMoreUsers exception

        :param page: the page to return
        :param users_per_page: the quantity of users per page
        :return: a list of serialized users and the quantity of pages
        """

    @abstractmethod
    def save_api_key(self, api_key: ApiKey):
        """
        Registers an api call made with an api key

        :param api_key: the api key
        """

    @abstractmethod
    def check_api_key(self, api_key: str) -> bool:
        """
        Checks if an api key is valid.

        :param api_key: the api key
        """

    @abstractmethod
    def register_api_call(self, api_key_str: str, path: str, method: str,
                          status: int, time: float, timestamp: datetime):
        """
        Registers an api call made with an api key

        :param api_key_str: the api key code
        :param path: the url path
        :param method: the method used
        :param status: the status code answer
        :param time: the time elapsed processing the api call
        :param timestamp: the date and time when the api call happened
        """

    @abstractmethod
    def get_api_calls_statistics(self) -> ApiCallsStatistics:
        """
        Computes the api call statistics

        @return: an object containing the api call statistics
        """


