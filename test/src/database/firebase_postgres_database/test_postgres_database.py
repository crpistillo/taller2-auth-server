from src.database.postgres_firebase_database import PostgresFirebaseDatabase
from src.model.user import User
from src.model.secured_password import SecuredPassword
import pytest
import firebase_admin
import os

@pytest.fixture(scope="function")
def postgres_firebase_database(monkeypatch, postgresql):
    def mockreturn(*args, **kwargs):
        return
    def mock_sign_in(*args, **kwargs):
        return "dummy_token"
    monkeypatch.setattr(firebase_admin.auth, "update_user", mockreturn)
    monkeypatch.setattr(firebase_admin.auth, "create_user", mockreturn)
    monkeypatch.setattr(firebase_admin.auth, "get_user_by_email", mockreturn)
    monkeypatch.setattr(firebase_admin.auth, "verify_id_token", mockreturn)
    PostgresFirebaseDatabase.__init__ = mockreturn
    PostgresFirebaseDatabase.sign_in_with_email_and_password = mock_sign_in
    database = PostgresFirebaseDatabase()
    database.conn = postgresql
    return database

def test_postgres(postgresql, postgres_firebase_database):

    print("asd")