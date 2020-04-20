import logging
from .database.database import Database
from .model.secured_password import SecuredPassword
from .model.user import User
from src.database.exceptions.user_not_found_error import UserNotFoundError
from src.model.exceptions.invalid_phone_number_error import InvalidPhoneNumberError
from src.model.exceptions.invalid_email_error import InvalidEmailError
from flask import request
from src.model.user_token import UserToken


USER_NOT_FOUND_MESSAGE = "User with email %s not found in the database"
USER_ALREADY_REGISTERED_MESSAGE = "User with email %s is already registered"
USER_INVALID_EMAIL_ERROR_MESSAGE = "Invalid email %s"
USER_INVALID_PHONE_ERROR_MESSAGE = "Invalid phone number %s for registration of %s"
WRONG_CREDENTIALS_MESSAGE = "Incorrect password when trying to log in"
GENERATING_TOKEN_MESSAGE = "Generating token for user with email %s"


class Controller:
    logger = logging.getLogger(__name__)
    def __init__(self, database: Database):
        """
        Here the init should receive all the parameters needed to know how to answer all the queries
        """
        self.database = database
        return

    def users_login(self):

        assert request.is_json
        content = request.get_json()

        try:
            user = self.database.search_user(content["email"])
            secured_password = SecuredPassword.from_raw_password(content["password"])

            if secured_password.__eq__(user.secured_password):
                self.logger.debug(GENERATING_TOKEN_MESSAGE % content["email"])
                user_token = UserToken.generate_token(content["email"])
                self.database.save_user_token(user_token)
                return user_token.token

            else:
                self.logger.info(WRONG_CREDENTIALS_MESSAGE)
                return WRONG_CREDENTIALS_MESSAGE

        except UserNotFoundError:
            self.logger.debug(USER_NOT_FOUND_MESSAGE % content["email"])
            return USER_NOT_FOUND_MESSAGE % content["email"], 400

    def users_recover_password(self):
        pass

    def users_new_password(self):
        pass

    def users_register(self):
        """
        Handles the user registration
        """
        assert request.is_json
        content = request.get_json()
        try:
            self.database.search_user(content["email"])
            return USER_ALREADY_REGISTERED_MESSAGE % content["email"], 400
        except UserNotFoundError:
            pass
        secured_password = SecuredPassword.from_raw_password(content["password"])
        try:
            user = User(email=content["email"], fullname=content["fullname"],
                        phone_number=content["phone_number"], photo=content["photo"],
                        secured_password=secured_password)
        except InvalidEmailError:
            self.logger.debug(USER_INVALID_EMAIL_ERROR_MESSAGE % content["email"])
            return USER_INVALID_EMAIL_ERROR_MESSAGE % content["email"], 400
        except InvalidPhoneNumberError:
            self.logger.debug(USER_INVALID_PHONE_ERROR_MESSAGE % (content["phone_number"], content["email"]))
            return USER_INVALID_PHONE_ERROR_MESSAGE % (content["phone_number"], content["email"]), 400
        self.database.save_user(user)
        return "OK"

    def get_user_field(self, field: str):
        """
        Gets an user field

        :param field: the field to search
        :return: the field wanted
        """
        # TODO: this does not work with other fields than phone_number, use the real code
        assert field == "phone_number"
        assert request.is_json
        content = request.get_json()
        try:
            user = self.database.search_user(content["email"])
        except UserNotFoundError:
            self.logger.debug(USER_NOT_FOUND_MESSAGE % content["email"])
            return USER_NOT_FOUND_MESSAGE % content["email"], 400
        return user.phone_number

    def users_profile_query(self):
        assert request.is_json
        content = request.get_json()
        try:
            user = self.database.search_user(content["email"])
        except UserNotFoundError:
            self.logger.debug(USER_NOT_FOUND_MESSAGE % content["email"])
            return USER_NOT_FOUND_MESSAGE % content["email"], 400

        serialized_user_dic = SerializedUser.from_user(user)._asdict()
        # remove_keys = ["password", "phone_number"]
        # [serialized_user_dic.pop(key) for key in remove_keys]
        return json.dumps(serialized_user_dic)

    def users_profile_update(self):
        pass

    def api_health(self):
        """
        A dumb api health

        :return: a tuple with the text and the status to return
        """
        self.logger.debug("Api health asked")
        return "Everything ok", 200