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
    admin: bool
    password: str

    @classmethod
    def from_user(cls, user: User) -> 'SerializedUser':
        return SerializedUser(email=user.get_email(),fullname=user.fullname,
                              phone_number=user.phone_number, photo=user.photo.get_base64(),
                              admin=user.is_admin(),
                              password=user.get_secured_password_string())

