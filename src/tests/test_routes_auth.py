import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from main import app
from src.tests.conftest import login_user_confirmed_true_and_hash_password
from src.database.models import User
from src.services.auth import auth_service
from src.database.db import get_db

@pytest.fixture
def client(session: Session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

@pytest.fixture
def user(session: Session):
    user = User(username="test_user", email="test@example.com", password="test_password", confirmed=True)
    login_user_confirmed_true_and_hash_password(user, session)
    return user

def test_login_user_invalid_email(client: TestClient, user: User):

    invalid_email = "invalid@example.com"
    invalid_password = "invalid_password"


    response = client.post("/api/login", data={"username": invalid_email, "password": invalid_password})

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}