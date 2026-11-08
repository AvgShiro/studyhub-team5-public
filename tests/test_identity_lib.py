from identity_lib import get_user, verify_token
from tests.conftest import login


def test_verify_token(client):
    token = login(client).json()["token"]
    info = verify_token(token)
    assert info["role"] == "student"


def test_verify_bad_token_returns_none():
    assert verify_token("garbage") is None


def test_get_user(client):
    uid = login(client).json()["user_id"]
    assert get_user(uid)["email"] == "student@th-deg.de"
    assert get_user(99999) is None
