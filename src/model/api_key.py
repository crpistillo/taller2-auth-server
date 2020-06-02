import datetime
import hashlib

class ApiKey:
    """
    Model entity for api keys
    """

    def __init__(self, alias: str):
        """

        :param alias: the alias of the owner of the key
        """
        self.alias = alias

    def get_api_key_hash(self) -> str:
        """
        Generates the api-key hash
        """
        return hashlib.md5(self.alias.encode()).hexdigest()

    def get_alias(self):
        """
        Return the api-key alias
        """
        return