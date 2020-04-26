from typing import NoReturn, Dict
from src.model.user import User
from src.model.user_recovery_token import UserRecoveryToken
from src.database.database import Database
from src.database.serialized.serialized_user import SerializedUser
from src.database.exceptions.user_not_found_error import UserNotFoundError
from src.model.secured_password import SecuredPassword
import psycopg2
import logging
import os

USER_INSERT_QUERY = """
INSERT INTO %s (email, fullname, phone_number, photo, password)
VALUES (%s, %s, %s, %s, %s)
"""

SEARCH_USER_QUERY = """SELECT email, fullname, phone_number, photo, password
FROM %s
WHERE email=%s
"""


class PostgresFirebaseDatabase(Database):
    """
    Postgres & Firebase implementation of Database abstraction
    """
    logger = logging.getLogger(__name__)
    def __init__(self, users_table_name: str, recovery_token_table_name: str, host_env_name: str,
                 user_env_name: str, pass_env_name: str, database_env_name: str):
        """

        :param users_table_name: the name of the table for querying users
        :param recovery_token_table_name: the name of the table for querying recovery tokens
        :param host_env_name: the env variable name for getting the host
        :param user_env_name: the env variable name for getting the user
        :param pass_env_name: the env variable name for getting the password
        :param database_env_name: the env variable name for getting the database name
        """
        self.users_table_name = users_table_name
        self.recovery_token_table_name = recovery_token_table_name
        self.conn = psycopg2.connect(host=os.environ[host_env_name], user=os.environ[user_env_name],
                                     password=os.environ[pass_env_name], database=os.environ[database_env_name])

    def save_user(self, user: User) -> NoReturn:
        """
        Saves an user
            if the user exists in the database it uploads its fields
            if the user does not exist it creates it with the corresponding fields

        :param user: the user to save
        """
        cursor = self.conn.cursor()
        serialized_user = SerializedUser.from_user(user)
        query = USER_INSERT_QUERY % (self.users_table_name, serialized_user.email, serialized_user.fullname,
                                     serialized_user.phone_number, serialized_user.photo, serialized_user.password)
        cursor.execute(query)
        cursor.close()


    def search_user(self, email: str) -> User:
        """
        Searches an user by its email
            if the user exists it returns a User
            if the user does not exist it raises a UserNotFoundError

        :param email: the email to search the user
        :return: an User object
        """
        cursor = self.conn.cursor()
        cursor.execute(SEARCH_USER_QUERY % (self.users_table_name, email))
        result = cursor.fetchone()
        secured_password = SecuredPassword(result[4])
        return User(email=result[0], fullname=result[1],
                    phone_number=result[2], photo=result[3],
                    secured_password=secured_password)

    def save_recovery_token(self, user_token: UserRecoveryToken) -> NoReturn:
        """
        Saves an user recovery token

        :param user_token: the user token to save
        """