import os
import tempfile

# Must be set BEFORE the app is imported, so tests use a throwaway database.
_tmp = tempfile.mkdtemp()
os.environ["TEAM5_DB_URL"] = f"sqlite:///{_tmp}/test.db"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app, seed_test_users


@pytest.fixture()
def client():
    # Fresh database for every test, so tests cannot affect each other.
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    seed_test_users()
    with TestClient(app) as c:
        yield c


def login(client, email="student@th-deg.de", password="test123"):
    return client.post("/auth/login", json={"email": email, "password": password})


def auth(client, email="student@th-deg.de", password="test123"):
    token = login(client, email, password).json()["token"]
    return {"Authorization": f"Bearer {token}"}
