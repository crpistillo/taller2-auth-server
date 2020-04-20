from flask import Flask
from src.controller import Controller
from logging.config import fileConfig
from src.database.ram_database import RamDatabase
from functools import partial


fileConfig('config/logging_conf.ini')


def create_application():
    controller = Controller(database=RamDatabase())
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
    app.add_url_rule('/users/profile_update', 'users_profile_update',
                     controller.users_profile_update, methods=['POST'])
    return app