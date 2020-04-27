import json
import logging

from .constants import messages
from .database.database import Database
from .database.exceptions.user_recovery_token_not_found_error import UserRecoveryTokenNotFoundError
from .model.secured_password import SecuredPassword
from .model.user import User
from src.database.exceptions.user_not_found_error import UserNotFoundError
from src.model.exceptions.invalid_phone_number_error import InvalidPhoneNumberError
from src.model.exceptions.invalid_email_error import InvalidEmailError
from src.database.serialized.serialized_user import SerializedUser
from flask import request
from src.model.user_recovery_token import UserRecoveryToken
from .services.email import EmailService


RECOVERY_TOKEN_SECRET = "dummy"


class Controller:
    logger = logging.getLogger(__name__)
    def __init__(self, database: Database):
        """
        Here the init should receive all the parameters needed to know how to answer all the queries
        """
        self.database = database
        return

    def users_login(self):
        """
        Handles the user login
        :return: a token if the credentials are ok
        """
        assert request.is_json
        content = request.get_json()
        try:
            user = self.database.search_user(content["email"])
        except UserNotFoundError:
            self.logger.debug(messages.USER_NOT_FOUND_MESSAGE % content["email"])
            return messages.USER_NOT_FOUND_MESSAGE % content["email"], 400
        secured_password = SecuredPassword.from_raw_password(content["password"])
        if user.password_match(secured_password):
            self.logger.debug(messages.GENERATING_LOGIN_TOKEN_MESSAGE % content["email"])
            return self.database.login(user)
        else:
            self.logger.info(messages.WRONG_CREDENTIALS_MESSAGE)
            return messages.WRONG_CREDENTIALS_MESSAGE, 400

    def users_recover_password(self):
        """
        Handles the user recovering
        :return: /a token for the user to generate a new password
        """
        assert request.is_json
        content = request.get_json()
        try:
            user = self.database.search_user(content["email"])
        except UserNotFoundError:
            self.logger.debug(messages.USER_NOT_FOUND_MESSAGE % content["email"])
            return messages.USER_NOT_FOUND_MESSAGE % content["email"], 400
        self.logger.debug(messages.GENERATING_RECOVERY_TOKEN_MESSAGE % content["email"])
        user_token = UserRecoveryToken.from_user(user, RECOVERY_TOKEN_SECRET)
        self.database.save_user_recovery_token(user_token)
        #return user_token.get_token()
        return EmailService.send_recovery_email(user, user_token)
        #TODO: fijarse si ya se creo un token de password-recovery para este usuario

    def users_new_password(self):
        """
        Handles the new password setting
        """
        assert request.is_json
        content = request.get_json()
        try:
            user = self.database.search_user(content["email"])
        except UserNotFoundError:
            self.logger.debug(messages.USER_NOT_FOUND_MESSAGE % content["email"])
            return messages.USER_NOT_FOUND_MESSAGE % content["email"], 400
        try:
            user_recovery_token = self.database.search_user_recovery_token(content["email"])
        except UserRecoveryTokenNotFoundError:
            self.logger.debug(messages.USER_RECOVERY_TOKEN_NOT_FOUND_MESSAGE % content["email"])
            return messages.USER_RECOVERY_TOKEN_NOT_FOUND_MESSAGE % content["email"], 400
        #TODO: implementar update
        if user_recovery_token.token_match(content["token"]):
            self.database.updatePassword(user, content["new_password"])
            self.logger.debug(messages.NEW_PASSWORD_SUCCESS_MESSAGE % content["email"])
            return messages.NEW_PASSWORD_SUCCESS_MESSAGE % content["email"], 200
        else:
            self.logger.info(messages.INVALID_TOKEN_MESSAGE % content["email"])
            return messages.INVALID_TOKEN_MESSAGE % content["email"], 400




    def users_register(self):
        """
        Handles the user registration
        """
        assert request.is_json
        content = request.get_json()
        try:
            self.database.search_user(content["email"])
            return messages.USER_ALREADY_REGISTERED_MESSAGE % content["email"], 400
        except UserNotFoundError:
            pass
        secured_password = SecuredPassword.from_raw_password(content["password"])
        try:
            user = User(email=content["email"], fullname=content["fullname"],
                        phone_number=content["phone_number"], photo=content["photo"],
                        secured_password=secured_password)
        except InvalidEmailError:
            self.logger.debug(messages.USER_INVALID_EMAIL_ERROR_MESSAGE % content["email"])
            return messages.USER_INVALID_EMAIL_ERROR_MESSAGE % content["email"], 400
        except InvalidPhoneNumberError:
            self.logger.debug(messages.USER_INVALID_PHONE_ERROR_MESSAGE % (content["phone_number"], content["email"]))
            return messages.USER_INVALID_PHONE_ERROR_MESSAGE % (content["phone_number"], content["email"]), 400
        self.database.save_user(user)
        return "OK"

    def users_profile_query(self):
        assert request.is_json
        content = request.get_json()
        try:
            user = self.database.search_user(content["email"])
        except UserNotFoundError:
            self.logger.debug(messages.USER_NOT_FOUND_MESSAGE % content["email"])
            return messages.USER_NOT_FOUND_MESSAGE % content["email"], 400

        serialized_user_dic = SerializedUser.from_user(user)._asdict()
        """
        #TODO: retrieve real photo
        serialized_user_dic["photo"] = ""
        return json.dumps({k:v for k,v in serialized_user_dic.items() if k!="password"})"""
        return json.dumps(serialized_user_dic)

    def api_health(self):
        """
        A dumb api health

        :return: a tuple with the text and the status to return
        """
        self.logger.debug("Api health asked")
        return "Everything ok", 200