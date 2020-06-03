from unittest import TestCase
from src.model.user_recovery_token import UserRecoveryToken
from src.model.user import User
from src.model.user import SecuredPassword
from src.model.photo import Photo

class TestUserRecoveryToken(TestCase):
    def setUp(self) -> None:
        self.user = User(email="cpistillo@fi.uba.ar", fullname="Carolina Pistillo",
                    phone_number="11 32453423", photo=Photo(),
                    secured_password=SecuredPassword.from_raw_password("carolina"))

    def test_tokens_not_equal_due_to_timestamp(self):

        token1 = UserRecoveryToken.from_user(self.user, "dummy")
        token2 = UserRecoveryToken.from_user(self.user, "dummy")
        self.assertNotEqual(token1.get_token(), token2.get_token())

    def test_get_token(self):
        token = UserRecoveryToken.from_user(self.user, "dummy")
        self.assertEqual(token.get_token(),token.token)

    def test_get_email(self):
        token = UserRecoveryToken.from_user(self.user, "dummy")
        self.assertEqual(token.get_email(),token.email)

