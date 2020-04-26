from flask import Flask
from src.controller import Controller
from logging.config import fileConfig
from src.database.ram_database import RamDatabase
from src.login_services.ram_login_service import RamLoginService
from config.load_config import load_config
from functools import partial
from typing import Optional


fileConfig('config/logging_conf.ini')

DEFAULT_CONFIG_FILE = "config/default_conf.yml"


def create_application(config_path: Optional[str] = None):
    """
    Creates the flask application

    :param config_path: the path to the configuration
    :return: a Flask app
    """
    if not config_path:
        config_path = DEFAULT_CONFIG_FILE
    config = load_config(config_path)
    controller = Controller(database=config.database, login_service=config.login_service)
    return create_application_with_controller(controller)

def create_application_with_controller(controller: Controller):
    app = Flask(__name__)
    app.add_url_rule('/health', 'api_health', controller.api_health)
    app.add_url_rule('/users/login', 'users_login', controller.users_login,
                     methods=["POST"])
    app.add_url_rule('/users/recover_password', 'users_recover_password',
                     controller.users_recover_password, methods=["POST"])
    app.add_url_rule('/users/new_password', 'users_recover_password',
                     controller.users_recover_password, methods=["POST"])
    app.add_url_rule('/users/register', 'users_register', controller.users_register,
                     methods=["POST"])
    app.add_url_rule('/users/profile_query', 'users_profile_query',
                     controller.users_profile_query, methods=['POST'])
    return app