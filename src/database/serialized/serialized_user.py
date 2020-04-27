from typing import NamedTuple
from src.model.user import User

class SerializedUser(NamedTuple):
    """
    It has the responsability of representing all the user data with strings
    """
    email: str
    fullname: str
    phone_number: str
    photo: str
    password: str

    @classmethod
    def from_user(cls, user: User) -> 'SerializedUser':
        return SerializedUser(email=user.email,fullname=user.fullname,
                              phone_number=user.phone_number, photo=user.photo,
                              password=user.secured_password.serialize())

