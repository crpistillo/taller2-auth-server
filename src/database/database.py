from typing import NoReturn, Tuple
from src.model.user import User
from abc import abstractmethod
from src.model.user_recovery_token import UserRecoveryToken
from src.model.secured_password import SecuredPassword
from src.database.serialized.serialized_user import SerializedUser
from typing import List

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

    def update_user(self, user: User, update_data) -> NoReturn:
        """
        Updates a user

        :param user: the user to update
        :param update_data: the parameters to update
        """
        if "password" in update_data:
            user.set_password(SecuredPassword.from_raw_password(update_data["password"]))
        if "fullname" in update_data:
            user.set_fullname(update_data["fullname"])
        if "phone_number" in update_data:
            user.set_phone_number(update_data["phone_number"])
        if "photo" in update_data:
            user.set_photo(update_data["photo"])

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

