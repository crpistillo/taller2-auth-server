import unittest
from src.model.user import User
from src.model.user import SecuredPassword
from src.model.exceptions.invalid_email_error import InvalidEmailError
from src.model.exceptions.invalid_phone_number_error import InvalidPhoneNumberError
from src.model.photo import Photo

class TestUnitsUser(unittest.TestCase):
    def setUp(self) -> None:
        self.secured_password = SecuredPassword.from_raw_password("password1")

    def testEmailValidation(self):
        with self.assertRaises(InvalidEmailError):
            User(email="asd", phone_number="+54 9 11 1111-1111", fullname="Pepito",
                 photo=Photo(), secured_password=self.secured_password)

    def testPhoneValidation(self):
        with self.assertRaises(InvalidPhoneNumberError):
            User(email="giancafferata@hotmail.com", phone_number="asd", fullname="Pepito",
                 photo=Photo(), secured_password=self.secured_password)

    def testPhoneValidationOnChange(self):
        valid_user = User(email="giancafferata@hotmail.com",
                          phone_number="+54 9 11 1111-1111", fullname="Pepito",
                          photo=Photo(), secured_password=self.secured_password)
        with self.assertRaises(InvalidPhoneNumberError):
            valid_user.set_phone_number("asd")