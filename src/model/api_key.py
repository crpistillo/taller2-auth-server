import datetime
import hashlib
from typing import Optional

class ApiKey:
    """
    Model entity for api keys
    """

    def __init__(self, alias: str, api_secret_generator: str,
                 health_endpoint: Optional[str]=None):
        """

        :param alias: the alias of the owner of the key
        :param api_secret_generator: a secret key
        :param health_endpoint: a health endpoint to ask for health status
        """
        self.alias = alias
        self.api_secret_generator = api_secret_generator
        self.health_endpoint = health_endpoint

    def get_api_key_hash(self) -> str:
        """
        Generates the api-key hash
        """
        return hashlib.md5((self.alias+self.api_secret_generator).encode()).hexdigest()

    def get_alias(self):
        """
        Return the api-key alias
        """
        return self.alias