from app import create_app
from app.extensions import db
from app.models.models import User
import pytest


@pytest.fixture
def logged_in_client():
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        WTF_CSRF_ENABLED=False,
    )
    with app.app_context():
        db.create_all()
        user = User(username="u1", email="u1@example.com")
        user.set_password("pass123")
        db.session.add(user)
        db.session.commit()

        client = app.test_client()
        client.post(
            "/auth/login",
            data={"username_or_email": "u1", "password": "pass123"},
            follow_redirects=True,
        )
        yield client
        db.drop_all()


def test_dashboard_requires_login(logged_in_client):
    res = logged_in_client.get("/dashboard")
    assert res.status_code == 200
