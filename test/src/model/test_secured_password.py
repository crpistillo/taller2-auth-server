import unittest
from src.model.secured_password import SecuredPassword

class TestUnitsSecuredPassword(unittest.TestCase):
    def testPasswordNotEqual(self):
        secured_password1 = SecuredPassword.from_raw_password("password1")
        secured_password2 = SecuredPassword.from_raw_password("password2")
        self.assertNotEqual(secured_password1, secured_password2)

    def testPasswordEqual(self):
        secured_password1 = SecuredPassword.from_raw_password("password")
        secured_password2 = SecuredPassword.from_raw_password("password")
        self.assertEqual(secured_password1, secured_password2)
