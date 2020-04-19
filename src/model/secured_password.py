import hashlib

class SecuredPassword:
    def __init__(self, state: str):
        """
        Initializes the password based on a serialized version of the object

        :param state: an string that represents the state of the password serialized
        """
        self.state = state

    def serialize(self) -> str:
        """
        Serializes the password data into a string safely

        :return: a representation of the password
        """
        return self.state

    @classmethod
    def from_raw_password(cls, raw_password: str) -> 'SecuredPassword':
        """
        Creates a secure password from a raw one

        :param raw_password: the password as the users would input it
        :return: a SecuredPassword
        """
        return cls(hashlib.md5(raw_password.encode("utf-8")).hexdigest())

    def __eq__(self, other: 'SecuredPassword') -> bool:
        """
        Responsible for comparing to SecuredPasswords

        :param other: other secured password
        :return: a boolean indicating if the password are equal
        """
        return other.state == self.state