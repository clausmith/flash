import os

import pytest

from app import create_app, db
from data.bootstrap import Bootstrap


@pytest.fixture
def app():
    app = create_app("testing")

    with app.app_context():
        db.create_all()
        Bootstrap.setup_default_user()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, email="admin@plinth.io", password="password"):
        return self._client.post("/auth/login", data={"email": email, "password": password})

    def logout(self):
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)
