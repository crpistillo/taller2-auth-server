import unittest
from src.database.ram_database import RamDatabase
from src.database.exceptions.user_not_found_error import UserNotFoundError
from src.database.exceptions.invalid_login_token import InvalidLoginToken
from src.model.user import User
from src.model.secured_password import SecuredPassword
from src.database.serialized.serialized_user import SerializedUser
from src.model.user_recovery_token import UserRecoveryToken
import datetime


class TestRamDatabase(unittest.TestCase):
    def setUp(self) -> None:
        self.ram_database = RamDatabase()
        secured_password = SecuredPassword.from_raw_password("password")
        self.test_user = User(email="giancafferata@hotmail.com", fullname="Gianmarco Cafferata",
                              phone_number="11 1111-1111", photo="", secured_password=secured_password)

    def test_user_does_not_exist_raises_error(self):
        with self.assertRaises(UserNotFoundError):
            self.ram_database.search_user("giancafferata@hotmail.com")

    def test_search_inexistent_user(self):
        self.ram_database.save_user(self.test_user)
        with self.assertRaises(UserNotFoundError):
            self.ram_database.search_user("jian01.cs@hotmail.com")

    def test_search_existent_user(self):
        self.ram_database.save_user(self.test_user)
        result_user = self.ram_database.search_user("giancafferata@hotmail.com")
        serialized_original_user = SerializedUser.from_user(self.test_user)
        serialized_queried_user = SerializedUser.from_user(result_user)
        self.assertEqual(serialized_original_user, serialized_queried_user)

    def test_modify_user(self):
        self.ram_database.save_user(self.test_user)
        result_user = self.ram_database.search_user("giancafferata@hotmail.com")
        serialized_queried_user = SerializedUser.from_user(result_user)
        self.assertEqual(serialized_queried_user.phone_number, "11 1111-1111")

        secured_password = SecuredPassword.from_raw_password("password")
        test_user2 = User(email="giancafferata@hotmail.com", fullname="Gianmarco Cafferata",
                          phone_number="11 2222-2222", photo="", secured_password=secured_password)
        self.ram_database.save_user(test_user2)

        result_user = self.ram_database.search_user("giancafferata@hotmail.com")
        serialized_queried_user = SerializedUser.from_user(result_user)
        self.assertEqual(serialized_queried_user.phone_number, "11 2222-2222")

    def test_token_does_not_exist_raises_error(self):
        with self.assertRaises(InvalidLoginToken):
            self.ram_database.get_user_by_token("token")

    def test_get_user_by_token(self):
        self.ram_database.save_user(self.test_user)
        token = self.ram_database.login(self.test_user)
        result_user = self.ram_database.get_user_by_token(token)

        serialized_original_user = SerializedUser.from_user(self.test_user)
        serialized_queried_by_token_user = SerializedUser.from_user(result_user)
        self.assertEqual(serialized_original_user, serialized_queried_by_token_user)




