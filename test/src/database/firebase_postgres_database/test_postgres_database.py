from src.database.postgres_firebase_database import PostgresFirebaseDatabase
from src.model.user import User
from src.model.secured_password import SecuredPassword
import datetime
from src.model.user_recovery_token import UserRecoveryToken
from src.database.exceptions.user_not_found_error import UserNotFoundError
from src.database.exceptions.user_recovery_token_not_found_error import UserRecoveryTokenNotFoundError
from firebase_admin.exceptions import NotFoundError
from src.database.exceptions.no_more_users import NoMoreUsers
from src.database.exceptions.invalid_login_token import InvalidLoginToken
from src.model.api_key import ApiKey
import pytest
import firebase_admin
import psycopg2
from typing import NamedTuple
import requests
import os

test_user = User(email="giancafferata@hotmail.com", fullname="Gianmarco Cafferata",
                 phone_number="11 1111-1111", photo="", secured_password=SecuredPassword.from_raw_password("password"))

test_user2 = User(email="jian01.cs@hotmail.com", fullname="Gianmarco Cafferata",
                  phone_number="11 1111-1111", photo="", secured_password=SecuredPassword.from_raw_password("password"))

test_recovery_token = UserRecoveryToken(email="giancafferata@hotmail.com", token="token",
                                        timestamp=datetime.datetime.now().isoformat())


class MockResult(NamedTuple):
    uid: int


class FakePostgres(NamedTuple):
    closed: int


class ResponseFirebaseToken:
    def json(self):
        return {"idToken": "dumb_token"}

    def raise_for_status(self):
        return


@pytest.fixture(scope="function")
def postgres_firebase_database(monkeypatch, postgresql):
    monkeypatch.setattr(firebase_admin.auth, "update_user", lambda *args, **kwargs: None)
    monkeypatch.setattr(firebase_admin.auth, "create_user", lambda *args, **kwargs: None)
    monkeypatch.setattr(firebase_admin.auth, "get_user_by_email", lambda *args, **kwargs: MockResult(0))
    monkeypatch.setattr(firebase_admin.auth, "verify_id_token", lambda *args, **kwargs:
    {"email": "giancafferata@hotmail.com"})
    monkeypatch.setattr(firebase_admin.auth, "delete_user", lambda *args, **kwargs: None)
    monkeypatch.setattr(firebase_admin, "get_app", lambda *args, **kwargs: True)
    monkeypatch.setattr(firebase_admin, "initialize_app", lambda *args, **kwargs: None)
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: ResponseFirebaseToken())
    monkeypatch.setattr(firebase_admin.credentials.Certificate, "__init__", lambda *args, **kwargs: None)
    aux_connect = psycopg2.connect
    monkeypatch.setattr(psycopg2, "connect", lambda *args, **kwargs: FakePostgres(0))
    os.environ["DUMB_ENV_NAME"] = "{}"
    database = PostgresFirebaseDatabase(*(["DUMB_ENV_NAME"]*10))
    monkeypatch.setattr(psycopg2, "connect", aux_connect)
    with open("test/src/database/config/initialize_db.sql", "r") as initialize_query:
        cursor = postgresql.cursor()
        cursor.execute(initialize_query.read())
        postgresql.commit()
        cursor.close()
    database.conn = postgresql
    database.users_table_name = "chotuve.users"
    database.recovery_token_table_name = "chotuve.user_recovery_token"
    database.api_key_table_name = "chotuve.api_keys"
    database.api_calls_table_name = "chotuve.api_key_calls"
    return database

def test_postgres_connection_error(monkeypatch, postgres_firebase_database):
    aux_connect = psycopg2.connect
    monkeypatch.setattr(psycopg2, "connect", lambda *args, **kwargs: FakePostgres(1))
    with pytest.raises(ConnectionError):
        database = PostgresFirebaseDatabase(*(["DUMB_ENV_NAME"] * 10))
    monkeypatch.setattr(psycopg2, "connect", aux_connect)

def test_firebase_connection_error(monkeypatch, postgres_firebase_database):
    aux_connect = psycopg2.connect
    monkeypatch.setattr(psycopg2, "connect", lambda *args, **kwargs: FakePostgres(0))
    monkeypatch.setattr(firebase_admin, "get_app", lambda *args, **kwargs: None)
    with pytest.raises(ConnectionError):
        database = PostgresFirebaseDatabase(*(["DUMB_ENV_NAME"] * 10))
    monkeypatch.setattr(psycopg2, "connect", aux_connect)

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

def test_delete_user(postgres_firebase_database):
    postgres_firebase_database.save_user(test_user)
    user = postgres_firebase_database.search_user("giancafferata@hotmail.com")
    assert user.get_email() == "giancafferata@hotmail.com"
    assert user.get_secured_password_string() == test_user.get_secured_password_string()
    postgres_firebase_database.delete_user("giancafferata@hotmail.com")
    with pytest.raises(UserNotFoundError):
        postgres_firebase_database.search_user("giancafferata@hotmail.com")

def test_update_user(postgres_firebase_database):
    postgres_firebase_database.save_user(test_user)
    postgres_firebase_database.update_user(test_user, {"password": "asd123"})
    user = postgres_firebase_database.search_user("giancafferata@hotmail.com")
    assert user.get_secured_password_string() == SecuredPassword.from_raw_password("asd123").serialize()
    postgres_firebase_database.update_user(test_user, {"fullname": "Pepe"})
    user = postgres_firebase_database.search_user("giancafferata@hotmail.com")
    assert user.fullname == "Pepe"
    postgres_firebase_database.update_user(test_user, {"phone_number": "1111"})
    user = postgres_firebase_database.search_user("giancafferata@hotmail.com")
    assert user.phone_number == "1111"

def test_login_with_existent_user(postgres_firebase_database):
    postgres_firebase_database.save_user(test_user)
    token = postgres_firebase_database.login(test_user)
    assert token == "dumb_token"
    user = postgres_firebase_database.get_user_by_token(token)
    assert user.get_email() == test_user.get_email()

def test_save_user_not_found_in_firebase(monkeypatch, postgres_firebase_database):
    postgres_firebase_database.save_user(test_user)
    def raise_not_found(*args, **kwargs):
        raise NotFoundError("")
    monkeypatch.setattr(firebase_admin.auth, "update_user", raise_not_found)
    postgres_firebase_database.update_user(test_user, {"password": "asd123"})
    monkeypatch.setattr(firebase_admin.auth, "update_user", lambda *args, **kwargs: None)

def test_list_no_more_users(postgres_firebase_database):
    with pytest.raises(NoMoreUsers):
        postgres_firebase_database.get_users(1,1)

def test_list_one_user(postgres_firebase_database):
    postgres_firebase_database.save_user(test_user)
    postgres_firebase_database.save_user(test_user2)
    users, pages = postgres_firebase_database.get_users(0,2)
    assert users[0].email == "giancafferata@hotmail.com"
    assert users[1].email == "jian01.cs@hotmail.com"
    assert pages == 1

def test_unexistent_login_token(monkeypatch, postgres_firebase_database):
    def value_error(*args, **kwargs):
        raise ValueError
    monkeypatch.setattr(firebase_admin.auth, "verify_id_token", value_error)
    with pytest.raises(InvalidLoginToken):
        postgres_firebase_database.get_user_by_token("")

def test_unexistent_api_key_invalid(postgres_firebase_database):
    assert not postgres_firebase_database.check_api_key("api key string")

def test_api_key_valid(postgres_firebase_database):
    api_key = ApiKey("test", "dumb")
    postgres_firebase_database.save_api_key(api_key)
    assert postgres_firebase_database.check_api_key(api_key.get_api_key_hash())