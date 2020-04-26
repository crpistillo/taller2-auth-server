from typing import NamedTuple
from src.database.database import Database
from src.login_services.login_service import LoginService
from yaml import load
from yaml import Loader

class AuthServerConfig(NamedTuple):
    database: Database
    login_service: LoginService


def load_config(config_path: str) -> AuthServerConfig:
    """
    Loads the config for the server

    :param config_path: the path where to load the config
    :return: an AuthServerConfig
    """
    with open(config_path, "r") as yaml_file:
        config_dict = load(yaml_file, Loader=Loader)

    database_name = config_dict["database"]
    database = Database.factory(database_name, **config_dict["databases"][database_name])

    login_service_name = config_dict["login_service"]
    login_service = LoginService.factory(login_service_name, **config_dict["login_services"][login_service_name])

    return AuthServerConfig(database=database, login_service=login_service)
