import pytest
from app import create_app
from app.extensions import db


@pytest.fixture
def client():
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        WTF_CSRF_ENABLED=False,
    )
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


def test_register_and_login(client):
    # Register
    res = client.post(
        "/auth/register",
        data={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )
    assert res.status_code == 200

    # Login
    res = client.post(
        "/auth/login",
        data={"username_or_email": "testuser", "password": "password123"},
        follow_redirects=True,
    )
    assert b"Logged in successfully" in res.data
