from src.database.postgres_firebase_database import PostgresFirebaseDatabase
from src.model.user import User
from src.model.secured_password import SecuredPassword
import datetime
from src.model.user_recovery_token import UserRecoveryToken
from src.database.exceptions.user_not_found_error import UserNotFoundError
from src.database.exceptions.user_recovery_token_not_found_error import UserRecoveryTokenNotFoundError
import pytest
import firebase_admin
from typing import NamedTuple
import os

test_user = User(email="giancafferata@hotmail.com", fullname="Gianmarco Cafferata",
                 phone_number="11 1111-1111", photo="", secured_password=SecuredPassword.from_raw_password("password"))

test_recovery_token = UserRecoveryToken(email="giancafferata@hotmail.com", token="token",
                                        timestamp=datetime.datetime.now().isoformat())

@pytest.fixture(scope="function")
def postgres_firebase_database(monkeypatch, postgresql):
    def mockreturn(*args, **kwargs):
        return
    def mock_get_user_by_email(*args, **kwargs):
        class MockResult(NamedTuple):
            uid: int
        return MockResult(0)
    def mock_sign_in(*args, **kwargs):
        return "dummy_token"
    monkeypatch.setattr(firebase_admin.auth, "update_user", mockreturn)
    monkeypatch.setattr(firebase_admin.auth, "create_user", mockreturn)
    monkeypatch.setattr(firebase_admin.auth, "get_user_by_email", mock_get_user_by_email)
    monkeypatch.setattr(firebase_admin.auth, "verify_id_token", mockreturn)
    PostgresFirebaseDatabase.__init__ = mockreturn
    PostgresFirebaseDatabase.sign_in_with_email_and_password = mock_sign_in
    database = PostgresFirebaseDatabase()
    with open("test/src/database/config/initialize_db.sql", "r") as initialize_query:
        cursor = postgresql.cursor()
        cursor.execute(initialize_query.read())
        postgresql.commit()
        cursor.close()
    database.conn = postgresql
    database.users_table_name = "chotuve.users"
    database.recovery_token_table_name = "chotuve.user_recovery_token"
    return database

def test_unexistent_user(postgres_firebase_database):
    with pytest.raises(UserNotFoundError):
        postgres_firebase_database.search_user("giancafferata@hotmail.com")

def test_search_existent_user(postgres_firebase_database):
    postgres_firebase_database.save_user(test_user)
    user = postgres_firebase_database.search_user("giancafferata@hotmail.com")
    assert user.get_email() == "giancafferata@hotmail.com"
    assert user.get_secured_password_string() == test_user.get_secured_password_string()

def test_unexistent_recovery_token(postgres_firebase_database):
    with pytest.raises(UserRecoveryTokenNotFoundError):
        postgres_firebase_database.search_user_recovery_token("giancafferata@hotmail.com")

def test_get_recovery_token(postgres_firebase_database):
    postgres_firebase_database.save_user(test_user)
    postgres_firebase_database.save_user_recovery_token(test_recovery_token)
    token = postgres_firebase_database.search_user_recovery_token("giancafferata@hotmail.com")
    assert token.get_email() == "giancafferata@hotmail.com"
    assert token.get_token() == "token"