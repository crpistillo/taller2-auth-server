import json
import logging
from typing import Optional
from .constants import messages
from .database.database import Database
from .database.exceptions.user_recovery_token_not_found_error import UserRecoveryTokenNotFoundError
from .model.secured_password import SecuredPassword
from .model.user import User
from src.database.exceptions.user_not_found_error import UserNotFoundError
from src.model.exceptions.invalid_phone_number_error import InvalidPhoneNumberError
from src.model.exceptions.invalid_email_error import InvalidEmailError
from src.database.serialized.serialized_user import SerializedUser
from src.database.exceptions.invalid_login_token import InvalidLoginToken
from flask import request
from src.model.user_recovery_token import UserRecoveryToken
from .services.email import EmailService
from flask_cors import cross_origin
from flask_httpauth import HTTPTokenAuth

auth = HTTPTokenAuth(scheme='Bearer')

RECOVERY_TOKEN_SECRET = "dummy"
LOGIN_MANDATORY_FIELDS = {"email", "password"}
RECOVER_PASSWORD_MANDATORY_FIELDS = {"email"}
NEW_PASSWORD_MANDATORY_FIELDS = {"email", "new_password", "token"}
USERS_REGISTER_MANDATORY_FIELDS = {"email", "password", "phone_number", "fullname", "photo"}


class Controller:
    logger = logging.getLogger(__name__)
    def __init__(self, database: Database, email_service: EmailService):
        """
        Here the init should receive all the parameters needed to know how to answer all the queries
        """

        @auth.verify_token
        def verify_token(token) -> Optional[User]:
            """
            Verifies a token

            :param token: the token to verify
            :return: the corresponding user
            """
            try:
                return self.database.get_user_by_token(token)
            except InvalidLoginToken:
                return

        self.database = database
        self.email_service = email_service

    @cross_origin()
    def users_login(self):
        """
        Handles the user login
        :return: a token if the credentials are ok
        """
        try:
            assert request.is_json
        except AssertionError:
            self.logger.debug(messages.REQUEST_IS_NOT_JSON)
            return messages.ERROR_JSON % messages.REQUEST_IS_NOT_JSON, 400
        content = request.get_json()
        if not LOGIN_MANDATORY_FIELDS.issubset(content.keys()):
            self.logger.debug(messages.MISSING_FIELDS_ERROR)
            return messages.ERROR_JSON % messages.MISSING_FIELDS_ERROR, 400
        try:
            user = self.database.search_user(content["email"])
        except UserNotFoundError:
            self.logger.debug(messages.USER_NOT_FOUND_MESSAGE % content["email"])
            return messages.ERROR_JSON % (messages.USER_NOT_FOUND_MESSAGE % content["email"]), 404
        secured_password = SecuredPassword.from_raw_password(content["password"])
        if user.password_match(secured_password):
            self.logger.debug(messages.GENERATING_LOGIN_TOKEN_MESSAGE % content["email"])
            return json.dumps({"login_token": self.database.login(user)})
        else:
            self.logger.info(messages.WRONG_CREDENTIALS_MESSAGE)
            return messages.ERROR_JSON % messages.WRONG_CREDENTIALS_MESSAGE, 403

    @cross_origin()
    def users_recover_password(self):
        """
        Handles the user recovering
        :return: a token for the user to generate a new password
        """
        try:
            assert request.is_json
        except AssertionError:
            self.logger.debug(messages.REQUEST_IS_NOT_JSON)
            return messages.ERROR_JSON % messages.REQUEST_IS_NOT_JSON, 400
        content = request.get_json()
        if not RECOVER_PASSWORD_MANDATORY_FIELDS.issubset(content.keys()):
            self.logger.debug(messages.MISSING_FIELDS_ERROR)
            return messages.ERROR_JSON % messages.MISSING_FIELDS_ERROR, 400
        try:
            user = self.database.search_user(content["email"])
        except UserNotFoundError:
            self.logger.debug(messages.USER_NOT_FOUND_MESSAGE % content["email"])
            return messages.ERROR_JSON % (messages.USER_NOT_FOUND_MESSAGE % content["email"]), 404
        self.logger.debug(messages.GENERATING_RECOVERY_TOKEN_MESSAGE % content["email"])
        user_token = UserRecoveryToken.from_user(user, RECOVERY_TOKEN_SECRET)
        self.database.save_user_recovery_token(user_token)
        self.email_service.send_recovery_email(user, user_token)
        return messages.SUCCESS_JSON

    @cross_origin()
    def users_new_password(self):
        """
        Handles the new password setting
        """
        try:
            assert request.is_json
        except AssertionError:
            self.logger.debug(messages.REQUEST_IS_NOT_JSON)
            return messages.ERROR_JSON % messages.REQUEST_IS_NOT_JSON, 400
        content = request.get_json()
        if not NEW_PASSWORD_MANDATORY_FIELDS.issubset(content.keys()):
            self.logger.debug(messages.MISSING_FIELDS_ERROR)
            return messages.ERROR_JSON % messages.MISSING_FIELDS_ERROR, 400
        try:
            user = self.database.search_user(content["email"])
        except UserNotFoundError:
            self.logger.debug(messages.USER_NOT_FOUND_MESSAGE % content["email"])
            return messages.ERROR_JSON % (messages.USER_NOT_FOUND_MESSAGE % content["email"]), 404
        try:
            user_recovery_token = self.database.search_user_recovery_token(content["email"])
        except UserRecoveryTokenNotFoundError:
            self.logger.debug(messages.USER_RECOVERY_TOKEN_NOT_FOUND_MESSAGE % content["email"])
            return messages.ERROR_JSON % (messages.USER_RECOVERY_TOKEN_NOT_FOUND_MESSAGE % content["email"]), 400
        if user_recovery_token.token_match(content["token"]):
            user.set_password(SecuredPassword.from_raw_password(content["new_password"]))
            self.database.save_user(user)
            self.logger.debug(messages.NEW_PASSWORD_SUCCESS_MESSAGE % content["email"])
            return messages.SUCCESS_JSON
        else:
            self.logger.debug(messages.INVALID_TOKEN_MESSAGE % content["email"])
            return messages.ERROR_JSON % (messages.INVALID_TOKEN_MESSAGE % content["email"]), 400

    @cross_origin()
    def users_register(self):
        """
        Handles the user registration
        """
        try:
            assert request.is_json
        except AssertionError:
            self.logger.debug(messages.REQUEST_IS_NOT_JSON)
            return messages.ERROR_JSON % messages.REQUEST_IS_NOT_JSON, 400
        content = request.get_json()
        if not USERS_REGISTER_MANDATORY_FIELDS.issubset(content.keys()):
            self.logger.debug(messages.MISSING_FIELDS_ERROR)
            return messages.ERROR_JSON % messages.MISSING_FIELDS_ERROR, 400
        try:
            self.database.search_user(content["email"])
            return messages.ERROR_JSON % (messages.USER_ALREADY_REGISTERED_MESSAGE % content["email"]), 400
        except UserNotFoundError:
            pass
        secured_password = SecuredPassword.from_raw_password(content["password"])
        try:
            user = User(email=content["email"], fullname=content["fullname"],
                        phone_number=content["phone_number"], photo=content["photo"],
                        secured_password=secured_password)
        except InvalidEmailError:
            self.logger.debug(messages.USER_INVALID_EMAIL_ERROR_MESSAGE % content["email"])
            return messages.ERROR_JSON % (messages.USER_INVALID_EMAIL_ERROR_MESSAGE % content["email"]), 400
        except InvalidPhoneNumberError:
            self.logger.debug(messages.USER_INVALID_PHONE_ERROR_MESSAGE % (content["phone_number"], content["email"]))
            return messages.ERROR_JSON % (messages.USER_INVALID_PHONE_ERROR_MESSAGE %
                                 (content["phone_number"], content["email"])), 400
        self.database.save_user(user)
        return messages.SUCCESS_JSON

    @cross_origin()
    @auth.login_required
    def users_profile_query(self):
        email_query = request.args.get('email')
        if email_query != auth.current_user().get_email() and not auth.current_user().is_admin():
            self.logger.debug(messages.USER_NOT_AUTHORIZED_ERROR)
            return messages.ERROR_JSON % messages.USER_NOT_AUTHORIZED_ERROR, 403
        if not email_query:
            self.logger.debug(messages.MISSING_FIELDS_ERROR)
            return messages.ERROR_JSON % messages.MISSING_FIELDS_ERROR, 400
        try:
            user = self.database.search_user(email_query)
        except UserNotFoundError:
            self.logger.debug(messages.USER_NOT_FOUND_MESSAGE % email_query)
            return messages.ERROR_JSON % (messages.USER_NOT_FOUND_MESSAGE % email_query), 404

        serialized_user_dic = SerializedUser.from_user(user)._asdict()
        return json.dumps(serialized_user_dic)

    @cross_origin()
    def api_health(self):
        """
        A dumb api health

        :return: a tuple with the text and the status to return
        """
        self.logger.debug("Api health asked")
        return messages.SUCCESS_JSON, 200