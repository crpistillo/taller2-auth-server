from io import BytesIO
from .secured_password import SecuredPassword

class User:
    """
    Model entity for the user
    """
    email: str
    fullname: str
    phone_number: str
    photo: str
    password: SecuredPassword
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
        # TODO: validations
        self.email = email
        self.fullname = fullname
        self.phone_number = phone_number
        self.photo = photo
        self.secured_password = secured_password