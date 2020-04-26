from typing import NamedTuple
from src.database.database import Database
from yaml import load
from yaml import Loader

class AuthServerConfig(NamedTuple):
    database: Database


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

    return AuthServerConfig(database=database)
