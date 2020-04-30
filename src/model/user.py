from .secured_password import SecuredPassword
from .exceptions.invalid_phone_number_error import InvalidPhoneNumberError
from .exceptions.invalid_email_error import InvalidEmailError
import re

PHONE_NUMBER_REGEX = "\+?(\s|-|\d)+"
EMAIL_REGEX = "[^@]+@[^\.]+\..+"


class User:
    """
    Model entity for the user
    """
    email: str
    fullname: str
    phone_number: str
    photo: str
    secured_password: SecuredPassword
    def __init__(self, email: str, fullname: str, phone_number: str, photo: str,
                 secured_password: SecuredPassword):
        """
        User initializer

        :param email: the email of the user
        :param fullname: the fullname of the user
        :param phone_number: the phone number of the user
        :param photo: the photo as bytes
        :param secured_password: a SecuredPassword object
        """
        if not re.fullmatch(PHONE_NUMBER_REGEX, phone_number, re.IGNORECASE):
            raise InvalidPhoneNumberError
        if not re.fullmatch(EMAIL_REGEX, email, re.IGNORECASE):
            raise InvalidEmailError
        self.email = email
        self.fullname = fullname
        self.phone_number = phone_number
        self.photo = photo
        self.secured_password = secured_password

    def get_email(self) -> str:
        return self.email

    def get_secured_password_string(self) -> str:
        return self.secured_password.serialize()

    def set_password(self, secured_password: SecuredPassword):
        self.secured_password = secured_password

    def password_match(self, other: SecuredPassword) -> bool:
        """
        Responsible for comparing to SecuredPasswords

        :param other: other secured password
        :return: a boolean indicating if the password are equal
        """
        return other.__eq__(self.secured_password)

