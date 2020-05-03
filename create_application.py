from flask import Flask, send_from_directory
from src.controller import Controller
from logging.config import fileConfig
from config.load_config import load_config
from typing import Optional
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS


fileConfig('config/logging_conf.ini')

DEFAULT_CONFIG_FILE = "config/default_conf.yml"
SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"


def create_application(config_path: Optional[str] = None):
    """
    Creates the flask application

    :param config_path: the path to the configuration
    :return: a Flask app
    """
    if not config_path:
        config_path = DEFAULT_CONFIG_FILE
    config = load_config(config_path)
    controller = Controller(database=config.database, email_service=config.email_service)
    return create_application_with_controller(controller)

def create_application_with_controller(controller: Controller):
    app = Flask(__name__)
    # Swagger UI
    @app.route('/static/<path:path>')
    def send_static(path):
        return send_from_directory("static", path)

    swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL,
                                                  config= {"app_name": "Chotuve Auth Server"})

    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    cors = CORS(app, resources={"/user": {"origins": "*"},
                                "/user/recover_password": {"origins": "*"},
                                "/user/new_password": {"origins": "*"},
                                "/user/login": {"origins": "*"},
                                "/health": {"origins": "*"}})

    app.add_url_rule('/health', 'api_health', controller.api_health)
    app.add_url_rule('/user/login', 'users_login', controller.users_login,
                     methods=["POST"])
    app.add_url_rule('/user/recover_password', 'users_recover_password',
                     controller.users_recover_password, methods=["POST"])
    app.add_url_rule('/user/new_password', 'users_new_password',
                     controller.users_new_password, methods=["POST"])
    app.add_url_rule('/user', 'users_register', controller.users_register,
                     methods=["POST"])
    app.add_url_rule('/user', 'users_profile_query',
                     controller.users_profile_query, methods=['GET'])
    app.add_url_rule('/user', 'users_profile_update', controller.users_profile_update,
                     methods=["PUT"])
    app.add_url_rule('/user', 'users_delete', controller.users_delete,
                     methods=["DELETE"])
    app.add_url_rule('/registered_users', 'registered_users', controller.registered_users,
                     methods=["GET"])



    return app