from tests.conftest import auth, login


def test_login_ok(client):
    r = login(client)
    assert r.status_code == 200
    assert r.json()["role"] == "student"


def test_login_wrong_password(client):
    assert login(client, password="nope").status_code == 401


def test_login_unknown_user(client):
    assert login(client, email="nobody@th-deg.de").status_code == 401


def test_me_needs_token(client):
    assert client.get("/users/me").status_code == 401


def test_me_has_no_password(client):
    body = client.get("/users/me", headers=auth(client)).json()
    assert body["email"] == "student@th-deg.de"
    assert "password" not in body and "password_hash" not in body


def test_garbage_token_rejected(client):
    r = client.get("/users/me", headers={"Authorization": "Bearer garbage"})
    assert r.status_code == 401


def test_update_name(client):
    h = auth(client)
    r = client.patch("/users/me", json={"name": "New Name"}, headers=h)
    assert r.json()["name"] == "New Name"
