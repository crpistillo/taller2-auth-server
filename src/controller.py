import json
import logging
from logging import Logger
from typing import Optional, Callable, List, Tuple, Any, Dict
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
from src.database.exceptions.no_more_users import NoMoreUsers
from flask import request
from src.model.user_recovery_token import UserRecoveryToken
from .services.email import EmailService
from flask_cors import cross_origin
from flask_httpauth import HTTPTokenAuth
from timeit import default_timer as timer
from functools import partial
from src.model.api_key import ApiKey
from src.model.photo import Photo
from flask import render_template_string
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.layouts import row
import math
from src.model.api_calls_statistics import ApiCallsStatistics
import datetime
import os

auth = HTTPTokenAuth(scheme='Bearer')

RECOVERY_TOKEN_SECRET = "dummy"
LOGIN_MANDATORY_FIELDS = {"email", "password"}
API_KEY_CREATE_MANDATORY_FIELDS = {"alias", "secret"}
RECOVER_PASSWORD_MANDATORY_FIELDS = {"email"}
NEW_PASSWORD_MANDATORY_FIELDS = {"email", "new_password", "token"}
USERS_REGISTER_MANDATORY_FIELDS = {"email", "password", "phone_number", "fullname"}


class Controller:
    logger = logging.getLogger(__name__)
    def __init__(self, database: Database, email_service: EmailService,
                 api_key_secret_generator_env_name: str):
        """
        Here the init should receive all the parameters needed to know how to answer all the queries

        :param database: the database to use
        :param email_service: email sending service
        :param api_key_secret_generator_env_name:
        the name of the env variable containing the api key secret generator
        """
        global uses_api_key

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
        self.api_key_secret_generator = os.environ[api_key_secret_generator_env_name]
        api_key_decorator = partial(self.api_key_decorator, self.logger, database)
        self.users_recover_password = api_key_decorator(self.users_recover_password)
        self.users_login = api_key_decorator(self.users_login)
        self.users_new_password = api_key_decorator(self.users_new_password)
        self.users_register = api_key_decorator(self.users_register)
        self.users_profile_query = api_key_decorator(self.users_profile_query)
        self.users_profile_update = api_key_decorator(self.users_profile_update)
        self.users_delete = api_key_decorator(self.users_delete)
        self.registered_users = api_key_decorator(self.registered_users)
        self.user_login_token_query = api_key_decorator(self.user_login_token_query)
        self.api_health = api_key_decorator(self.api_health)

    @staticmethod
    def api_key_decorator(logger: Logger, database: Database,
                          func: Callable):
        def wrapper():
            api_key = request.args.get('api_key')
            if not api_key:
                logger.debug(messages.API_KEY_NOT_FOUND)
                return messages.ERROR_JSON % messages.API_KEY_NOT_FOUND, 401
            if database.check_api_key(api_key):
                start = timer()
                result = func()
                database.register_api_call(api_key, request.path, request.method, result.status_code,
                                           timer()-start, datetime.datetime.now())
                return result
            else:
                logger.debug(messages.API_KEY_INVALID)
                return messages.ERROR_JSON % messages.API_KEY_INVALID, 403
        return wrapper

    @cross_origin()
    def users_login(self):
        """
        Handles the user login
        :return: a json with the login_token on success or an error in another case
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
            user_dict = SerializedUser.from_user(user)._asdict()
            del user_dict["password"]
            return json.dumps({"login_token": self.database.login(user),
                               "user": user_dict})
        else:
            self.logger.debug(messages.WRONG_CREDENTIALS_MESSAGE)
            return messages.ERROR_JSON % messages.WRONG_CREDENTIALS_MESSAGE, 403

    @cross_origin()
    def users_recover_password(self):
        """
        Handles the user password recovering
        On success, it sends an email with the token for the user to generate a new password
        :return: a json with a success message on success or an error in another case
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
        return messages.SUCCESS_JSON, 200

    @cross_origin()
    def users_new_password(self):
        """
        Handles the new password setting
        :return: a json with a success message on success or an error in another case
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
            return messages.SUCCESS_JSON, 200
        else:
            self.logger.debug(messages.INVALID_TOKEN_MESSAGE % content["email"])
            return messages.ERROR_JSON % (messages.INVALID_TOKEN_MESSAGE % content["email"]), 400

    @cross_origin()
    def users_register(self):
        """
        Handles the user registration
        :return: a json with a success message on success or an error in another case
        """
        content = request.form
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
            photo = Photo()
            if 'photo' in request.files:
                photo = Photo.from_bytes(request.files['photo'].stream)
            user = User(email=content["email"], fullname=content["fullname"],
                        phone_number=content["phone_number"], photo=photo,
                        secured_password=secured_password)
        except InvalidEmailError:
            self.logger.debug(messages.USER_INVALID_EMAIL_ERROR_MESSAGE % content["email"])
            return messages.ERROR_JSON % (messages.USER_INVALID_EMAIL_ERROR_MESSAGE % content["email"]), 400
        except InvalidPhoneNumberError:
            self.logger.debug(messages.USER_INVALID_PHONE_ERROR_MESSAGE % (content["phone_number"], content["email"]))
            return messages.ERROR_JSON % (messages.USER_INVALID_PHONE_ERROR_MESSAGE %
                                 (content["phone_number"], content["email"])), 400
        self.database.save_user(user)
        return messages.SUCCESS_JSON, 200

    @cross_origin()
    @auth.login_required
    def users_profile_query(self):
        """
        Handles the user recovering
        :return: a json with the data of the requested user on success or an error in another case
        """
        email_query = request.args.get('email')
        if not email_query:
            self.logger.debug(messages.MISSING_FIELDS_ERROR)
            return messages.ERROR_JSON % messages.MISSING_FIELDS_ERROR, 400
        try:
            user = self.database.search_user(email_query)
        except UserNotFoundError:
            self.logger.debug(messages.USER_NOT_FOUND_MESSAGE % email_query)
            return messages.ERROR_JSON % (messages.USER_NOT_FOUND_MESSAGE % email_query), 404

        serialized_user_dic = SerializedUser.from_user(user)._asdict()
        return json.dumps(serialized_user_dic), 200

    @cross_origin()
    @auth.login_required
    def users_profile_update(self):
        """
        Handles updating a user's profile
        :return: a json with a success message on success or an error in another case
        """
        email_query = request.args.get('email')
        if not email_query:
            self.logger.debug(messages.MISSING_FIELDS_ERROR)
            return messages.ERROR_JSON % messages.MISSING_FIELDS_ERROR, 400
        if email_query != auth.current_user().get_email() and not auth.current_user().is_admin():
            self.logger.debug(messages.USER_NOT_AUTHORIZED_ERROR)
            return messages.ERROR_JSON % messages.USER_NOT_AUTHORIZED_ERROR, 403
        content = request.form
        try:
            user = self.database.search_user(email_query)
        except UserNotFoundError:
            self.logger.debug(messages.USER_NOT_FOUND_MESSAGE % email_query)
            return messages.ERROR_JSON % (messages.USER_NOT_FOUND_MESSAGE % email_query), 404
        password = SecuredPassword.from_raw_password(content["password"]) if "password" in content else None
        fullname = content["fullname"] if "fullname" in content else None
        phone_numer = content["phone_number"] if "phone_number" in content else None
        photo = Photo()
        if 'photo' in request.files:
            photo = Photo.from_bytes(request.files['photo'].stream)
        self.database.update_user(user, password=password, fullname=fullname,
                                  phone_number=phone_numer, photo=photo)
        return messages.SUCCESS_JSON, 200


    @cross_origin()
    @auth.login_required
    def users_delete(self):
        """
        Handles the delete of an user
        :return: a json with a success message on success or an error in another case
        """
        email_query = request.args.get('email')
        if not email_query:
            self.logger.debug(messages.MISSING_FIELDS_ERROR)
            return messages.ERROR_JSON % messages.MISSING_FIELDS_ERROR, 400
        if email_query != auth.current_user().get_email() and not auth.current_user().is_admin():
            self.logger.debug(messages.USER_NOT_AUTHORIZED_ERROR)
            return messages.ERROR_JSON % messages.USER_NOT_AUTHORIZED_ERROR, 403
        try:
            self.database.search_user(email_query)
        except UserNotFoundError:
            self.logger.debug(messages.USER_NOT_FOUND_MESSAGE % email_query)
            return messages.ERROR_JSON % (messages.USER_NOT_FOUND_MESSAGE % email_query), 404
        self.database.delete_user(email_query)
        return messages.SUCCESS_JSON, 200

    @cross_origin()
    @auth.login_required
    def registered_users(self):
        """
        Handles the return of all registered users
        return: a json with a list of dictionaries with the registered users data
                for the required page with a fixed users_per_page value
        """
        try:
            users_per_page = int(request.args.get('users_per_page'))
            page = int(request.args.get('page'))
        except TypeError:
            self.logger.debug(messages.MISSING_FIELDS_ERROR)
            return messages.ERROR_JSON % messages.MISSING_FIELDS_ERROR, 400
        if not auth.current_user().is_admin():
            self.logger.debug(messages.USER_NOT_AUTHORIZED_ERROR)
            return messages.ERROR_JSON % messages.USER_NOT_AUTHORIZED_ERROR, 403
        try:
            users, pages = self.database.get_users(page, users_per_page)
        except NoMoreUsers:
            self.logger.debug(messages.INVALID_PAGE_ACCESS_ERROR % page.__str__())
            return messages.ERROR_JSON % (messages.INVALID_PAGE_ACCESS_ERROR % page.__str__()), 400
        registered_users = {"results": [{k: v for k, v in user._asdict().items()
                                         if k != "password"}
                                        for user in users],
                            "pages": pages}
        return json.dumps(registered_users), 200

    @auth.login_required
    @cross_origin()
    def user_login_token_query(self):
        """
        Queries the user for a corresponding login token
        :return: a json containing the email which the login token corresponds to or an error
        """
        user = auth.current_user()
        serialized_user_dic = SerializedUser.from_user(user)._asdict()
        return json.dumps(serialized_user_dic), 200

    @cross_origin()
    def new_api_key(self):
        """
        Gets a new api key for a server
        :return a json containing the api key to be used
        """
        try:
            assert request.is_json
        except AssertionError:
            self.logger.debug(messages.REQUEST_IS_NOT_JSON)
            return messages.ERROR_JSON % messages.REQUEST_IS_NOT_JSON, 400
        content = request.get_json()
        if not API_KEY_CREATE_MANDATORY_FIELDS.issubset(content.keys()):
            self.logger.debug(messages.MISSING_FIELDS_ERROR)
            return messages.ERROR_JSON % messages.MISSING_FIELDS_ERROR, 400
        if not content["secret"] == self.api_key_secret_generator:
            self.logger.debug(messages.API_KEY_SECRET_INVALID)
            return messages.ERROR_JSON % messages.API_KEY_SECRET_INVALID, 403
        health_endpoint = "" if not "health_endpoint" in content else content["health_endpoint"]
        api_key = ApiKey(content["alias"], self.api_key_secret_generator,
                         health_endpoint)
        self.database.save_api_key(api_key)
        return json.dumps({"api_key": api_key.get_api_key_hash()}), 200

    @cross_origin()
    def show_statistics(self):
        """
        Show server statistics
        """
        plots = []
        api_calls_statistics = self.database.get_api_calls_statistics()
        median_response_time_plots = self.median_response_time_plots(api_calls_statistics)
        api_keys_by_call_plots = self.api_keys_by_call_plots(api_calls_statistics)
        for api_alias in median_response_time_plots.keys():
            plots += [median_response_time_plots[api_alias]]
            plots += [api_keys_by_call_plots[api_alias]]
        with open('static_html/dashboard.html', 'r') as template_file:
            template = template_file.read()
        return render_template_string(template, plots=plots)

    @staticmethod
    def median_response_time_plots(api_calls_statistics: ApiCallsStatistics) -> Dict[str, Tuple[Any, Any]]:
        """
        Returns a rendered line plots of median response time

        @param api_calls_statistics: the api call statistics
        @return: rendered plots
        """
        plots = {}
        median_response_statistics = api_calls_statistics.median_response_time_last_30_days()
        for api_alias in median_response_statistics.keys():
            dict_items = sorted(median_response_statistics[api_alias].items(), key=lambda x: x[0])
            plot = figure(plot_height=100, sizing_mode='scale_width',
                          title="Median response time from up to 30 days ago for '%s' server" % api_alias)
            x = [str(k) for k,_ in dict_items]
            y = [v for _,v in dict_items]
            plot.vbar(x=x, top=y, width=0.9)
            plots[api_alias] = components(plot)
        return plots

    @staticmethod
    def api_keys_by_call_plots(api_calls_statistics: ApiCallsStatistics) -> Dict[str, Tuple[Any, Any]]:
        """
        Returns rendered plots of api calls by type

        @param api_calls_statistics: the api call statistics
        @return: rendered plots
        """
        plots = {}
        api_calls_by_type = api_calls_statistics.api_calls_by_type()
        for api_alias in api_calls_by_type.keys():
            calls_by_path = api_calls_by_type[api_alias][0]
            calls_by_method = api_calls_by_type[api_alias][1]
            calls_by_status = api_calls_by_type[api_alias][2]

            labels, values = zip(*calls_by_path.items())
            s1 = figure(sizing_mode='scale_width', plot_height=300,x_range=list(labels),
                        title="Paths called by '%s' server" % api_alias)
            s1.vbar(x=list(labels), top=values, width=0.9)

            labels, values = zip(*calls_by_method.items())
            s2 = figure(sizing_mode='scale_width', plot_height=300,x_range=list(labels),
                        title="Methods called by '%s' server" % api_alias)
            s2.vbar(x=list(labels), top=values, width=0.9)

            labels, values = zip(*calls_by_status.items())
            s3 = figure(sizing_mode='scale_width', plot_height=300,x_range=[str(l) for l in labels],
                        title="Status received by '%s' server" % api_alias)
            s3.vbar(x=[str(l) for l in labels], top=values, width=0.9)

            plots[api_alias] = components(row(s1, s2, s3))
        return plots

    @cross_origin()
    def api_health(self):
        """
        A dumb api health

        :return: a tuple with the text and the status to return
        """
        return messages.SUCCESS_JSON, 200