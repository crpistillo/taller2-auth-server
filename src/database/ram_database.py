from typing import NoReturn, Dict, List, Tuple
from src.model.user import User
from src.model.user_recovery_token import UserRecoveryToken
from src.database.database import Database
from src.model.secured_password import SecuredPassword
from src.database.serialized.serialized_user import SerializedUser
from src.database.serialized.serialized_user_recovery_token import SerializedUserRecoveryToken
from src.database.exceptions.user_not_found_error import UserNotFoundError
from src.database.exceptions.user_recovery_token_not_found_error import UserRecoveryTokenNotFoundError
from src.database.exceptions.invalid_login_token import InvalidLoginToken
from src.database.exceptions.no_more_users import NoMoreUsers
from src.model.api_calls_statistics import ApiCallsStatistics, ApiKeyCall
from src.model.api_key import ApiKey
from src.model.photo import Photo
import logging
import hashlib
from operator import itemgetter
import math
from datetime import datetime

class RamDatabase(Database):
    """
    Ram implementation of Database abstraction
    """
    serialized_users: Dict[str, SerializedUser]
    serialized_user_recovery_tokens: Dict[str, SerializedUserRecoveryToken]
    logger = logging.getLogger(__module__)
    def __init__(self):
        self.serialized_users = {}
        self.serialized_user_recovery_tokens = {}
        self.tokens = {}
        self.api_keys = {}
        self.api_calls = {}

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
                    phone_number=serialized_user.phone_number, photo=Photo(serialized_user.photo),
                    secured_password=secured_password, admin=serialized_user.admin)

    def login(self, user: User) -> str:
        """
        Logins the user and generates a token valid for future actions

        :param user: the user to login
        :return: an string token for future authentication
        """
        token = hashlib.sha256(user.get_email().encode("utf-8")).hexdigest()
        self.logger.debug("Logging user with email %s" % user.get_email())
        self.tokens[token] = user.get_email()
        return token

    def get_user_by_token(self, login_token: str) -> User:
        """
        Gets the corresponding user fot a login token
            if the login token does not exists it returns a InvalidLoginToken exception

        :param login_token: the login token string
        :return: the user associated
        """
        self.logger.debug("Retrieving user by token")
        if login_token not in self.tokens:
            raise InvalidLoginToken
        return self.search_user(self.tokens[login_token])

    def save_user_recovery_token(self, user_recovery_token: UserRecoveryToken) -> NoReturn:
        """
        Saves an user recovery token

        :param user_recovery_token: the user token to save
        """
        serialized_user_recovery_token = SerializedUserRecoveryToken.from_user_recovery_token(user_recovery_token)
        self.logger.debug("Saving user recovery token with email %s" % serialized_user_recovery_token.email)
        self.serialized_user_recovery_tokens[serialized_user_recovery_token.email] = serialized_user_recovery_token

    def search_user_recovery_token(self, email: str) -> UserRecoveryToken:
        """
        Searches an user_recovery_token by its email
            if the user_recovery_token exists it returns a UserRecoveryToken
            if the token does not exist it raises a UserRecoveryTokenNotFoundError

        :param email: the email to search the user
        :return: an UserRecoveryToken object
        """
        if email not in self.serialized_user_recovery_tokens:
            raise UserRecoveryTokenNotFoundError
        self.logger.debug("Loading user_recovery_token with email %s" % email)
        serialized_user_recovery_token = self.serialized_user_recovery_tokens[email]
        return UserRecoveryToken(email=serialized_user_recovery_token.email, token=serialized_user_recovery_token.token,
                                 timestamp=serialized_user_recovery_token.timestamp)

    def delete_user(self, email: str) -> NoReturn:
        """
        Removes all user data from database

        :param email: the email of the user to be deleted
        """
        self.logger.debug("Deleting user with email %s" % email)
        if email in self.serialized_user_recovery_tokens:
            del self.serialized_user_recovery_tokens[email]
        del self.serialized_users[email]

    def get_users(self, page: int, users_per_page: int) -> Tuple[List[SerializedUser], int]:
        """
        Get a list of users paginated
            if there are no more pages returns a NoMoreUsers exception

        :param page: the page to return
        :param users_per_page: the quantity of users per page
        :return: a list of serialized users and the quantity of pages
        """
        self.logger.debug("Called get users for page %d with %d users per page" % (page, users_per_page))
        if len(self.serialized_users) == 0:
            return [], 0
        pages = math.ceil(len(self.serialized_users) / users_per_page)
        if pages <= page:
            raise NoMoreUsers
        start = page*users_per_page
        end = start + users_per_page
        list_of_users = sorted(list(self.serialized_users.values()), key=lambda x: x.email)
        return list_of_users[start:end], pages

    def save_api_key(self, api_key: ApiKey):
        """
        Registers an api call made with an api key

        :param api_key: the api key
        """
        self.api_keys[api_key.get_api_key_hash()] = api_key

    def check_api_key(self, api_key_str: str) -> bool:
        """
        Checks if an api key is valid.

        :param api_key_str: the api key code
        """
        return api_key_str in self.api_keys

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
        if api_key_str not in self.api_calls:
            self.api_calls[api_key_str] = []
        self.api_calls[api_key_str].append((path, method, status, time, timestamp))

    def get_api_calls_statistics(self) -> ApiCallsStatistics:
        """
        Computes the api call statistics

        @return: an object containing the api call statistics
        """
        api_calls_tuples = []
        for api_key in self.api_calls.keys():
            api_calls_tuples += [ApiKeyCall(self.api_keys[api_key].get_alias(), *call)
                                 for call in self.api_calls[api_key]]
        return ApiCallsStatistics(api_calls_tuples)
