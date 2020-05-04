from typing import NoReturn, Dict
from src.model.user import User
from src.model.user_recovery_token import UserRecoveryToken
from src.database.database import Database
from src.database.serialized.serialized_user import SerializedUser
from src.database.serialized.serialized_user_recovery_token import SerializedUserRecoveryToken
from src.database.exceptions.user_not_found_error import UserNotFoundError
from src.database.exceptions.user_recovery_token_not_found_error import UserRecoveryTokenNotFoundError
from src.model.secured_password import SecuredPassword
import psycopg2
import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
from firebase_admin.exceptions import NotFoundError
import logging
import os
import json
import requests

FIREBASE_LOGIN_API_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"

USER_INSERT_QUERY = """
INSERT INTO %s (email, fullname, phone_number, photo, password, admin)
VALUES ('%s', '%s', '%s', '%s', '%s', '%s')
ON CONFLICT (email) DO UPDATE 
  SET fullname = excluded.fullname, 
      phone_number = excluded.phone_number,
      photo = excluded.photo,
      password = excluded.password,
      admin = excluded.admin;
"""

SEARCH_USER_QUERY = """SELECT email, fullname, phone_number, photo, password, admin
FROM %s
WHERE email='%s'
"""

RECOVERY_TOKEN_INSERT_QUERY = """
INSERT INTO %s (email, token, timestamp)
VALUES ('%s', '%s', '%s')
ON CONFLICT (email) DO UPDATE 
  SET token = excluded.token, 
      timestamp = excluded.timestamp;
"""

RECOVERY_TOKEN_QUERY = """SELECT email, token, timestamp
FROM %s
WHERE email='%s';
"""

DELETE_USER_QUERY = """
DELETE FROM %s
WHERE email='%s';
DELETE FROM %s
WHERE email='%s';
"""

class PostgresFirebaseDatabase(Database):
    """
    Postgres & Firebase implementation of Database abstraction
    """
    logger = logging.getLogger(__name__)
    # TODO: avoid sql injection
    def __init__(self, users_table_name: str, recovery_token_table_name: str, postgr_host_env_name: str,
                 postgr_user_env_name: str, postgr_pass_env_name: str, postgr_database_env_name: str,
                 firebase_json_env_name: str, firebase_api_key_env_name: str):
        """

        :param users_table_name: the name of the table for querying users
        :param recovery_token_table_name: the name of the table for querying recovery tokens
        :param postgr_host_env_name: the env variable name for getting the host
        :param postgr_user_env_name: the env variable name for getting the user
        :param postgr_pass_env_name: the env variable name for getting the password
        :param postgr_database_env_name: the env variable name for getting the database name
        :param firebase_json_env_name: the env variable name containing the firebase sdk json credentials
        :param firebase_api_key_env_name: the env variable name containing the firebase api key
        """
        self.users_table_name = users_table_name
        self.recovery_token_table_name = recovery_token_table_name
        self.conn = psycopg2.connect(host=os.environ[postgr_host_env_name], user=os.environ[postgr_user_env_name],
                                     password=os.environ[postgr_pass_env_name],
                                     database=os.environ[postgr_database_env_name])
        if self.conn.closed == 0:
            self.logger.info("Connected to postgres database")
        else:
            self.logger.error("Unable to connect to postgres database")
            raise ConnectionError("Unable to connect to postgres database")
        cred = credentials.Certificate(json.loads(os.environ[firebase_json_env_name]))
        firebase_admin.initialize_app(cred)
        if firebase_admin.get_app():
            self.logger.info("Connected to firebase")
        else:
            self.logger.error("Unable to connect to firebase")
            raise ConnectionError("Unable to connect to firebase")
        self.firebase_api_key = os.environ[firebase_api_key_env_name]

    def save_user(self, user: User) -> NoReturn:
        """
        Saves an user
            if the user exists in the database it uploads its fields
            if the user does not exist it creates it with the corresponding fields

        :param user: the user to save
        """
        cursor = self.conn.cursor()
        serialized_user = SerializedUser.from_user(user)
        self.logger.debug("Saving user with email %s" % serialized_user.email)
        try:
            firebase_uid = auth.get_user_by_email("giancafferata@hotmail.com").uid
            auth.update_user(firebase_uid, **{"password": serialized_user.password})
        except NotFoundError:
            auth.create_user(**{"email": serialized_user.email, "password": serialized_user.password})

        query = USER_INSERT_QUERY % (self.users_table_name, serialized_user.email, serialized_user.fullname,
                                     serialized_user.phone_number, serialized_user.photo, serialized_user.password,
                                     serialized_user.admin)
        cursor.execute(query)
        self.conn.commit()
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
        self.logger.debug("Loading user with email %s" % email)
        cursor.execute(SEARCH_USER_QUERY % (self.users_table_name, email))
        result = cursor.fetchone()
        if not result:
            raise UserNotFoundError
        secured_password = SecuredPassword(result[4])
        cursor.close()
        #TODO: return the actual photo
        return User(email=result[0], fullname=result[1],
                    phone_number=result[2], photo="",
                    secured_password=secured_password,
                    admin=result[5])

    def sign_in_with_email_and_password(self, email: str, password: str) -> str:
        """
        Signs in a user through firebase API and returns an id token

        :param email: the user email
        :param password: the user password
        :return: an id token
        """
        payload = json.dumps({
            "email": email,
            "password": password,
            "returnSecureToken": True
        })

        r = requests.post(FIREBASE_LOGIN_API_URL,
                          params={"key": self.firebase_api_key},
                          data=payload)
        r.raise_for_status()

        return r.json()["idToken"]

    def login(self, user: User) -> str:
        """
        Logins the user and generates a token valid for future actions

        :param user: the user to login
        :return: an string token for future authentication
        """
        self.logger.debug("Logging user with email %s" % user.get_email())
        idToken = self.sign_in_with_email_and_password(user.get_email(), user.get_secured_password_string())
        return idToken

    def get_user_by_token(self, login_token: str) -> User:
        """
        Gets the corresponding user fot a login token
            if the login token does not exists it returns a InvalidLoginToken exception

        :param login_token: the login token string
        :return: the user associated
        """
        self.logger.debug("Retrieving user by token")
        user_email = auth.verify_id_token(login_token)["email"]
        return self.search_user(user_email)

    def save_user_recovery_token(self, user_recovery_token: UserRecoveryToken) -> NoReturn:
        """
        Saves an user recovery token

        :param user_recovery_token: the user token to save
        """
        serialized_user_recovery_token = SerializedUserRecoveryToken.from_user_recovery_token(user_recovery_token)
        self.logger.debug("Saving user recovery token with email %s" % serialized_user_recovery_token.email)
        cursor = self.conn.cursor()

        query = RECOVERY_TOKEN_INSERT_QUERY % (self.recovery_token_table_name, serialized_user_recovery_token.email,
                                               serialized_user_recovery_token.token,
                                               serialized_user_recovery_token.timestamp)
        cursor.execute(query)
        self.conn.commit()
        cursor.close()

    def search_user_recovery_token(self, email: str) -> UserRecoveryToken:
        """
        Searches an user_recovery_token by its email
            if the user_recovery_token exists it returns a UserRecoveryToken
            if the token does not exist it raises a UserRecoveryTokenNotFoundError

        :param email: the email to search the user
        :return: an UserRecoveryToken object
        """
        self.logger.debug("Loading user_recovery_token with email %s" % email)
        cursor = self.conn.cursor()
        cursor.execute(RECOVERY_TOKEN_QUERY % (self.recovery_token_table_name, email))
        result = cursor.fetchone()
        if not result:
            raise UserRecoveryTokenNotFoundError
        return UserRecoveryToken(result[0], result[1], result[2])


    def delete_user(self, email: str) -> NoReturn:
        """
        Removes all user data from database

        :param email: the email of the user to be deleted
        """
        self.logger.debug("Deleting user with email %s" % email)
        cursor = self.conn.cursor()
        cursor.execute(DELETE_USER_QUERY % (self.recovery_token_table_name, email,
                                            self.users_table_name, email))
        self.conn.commit()
        cursor.close()
        firebase_uid = auth.get_user_by_email("giancafferata@hotmail.com").uid
        auth.delete_user(firebase_uid)

