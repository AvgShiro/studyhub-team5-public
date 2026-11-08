from fastapi.testclient import TestClient
import mock_api

client = TestClient(mock_api.app)


def login(email, pw):
    return client.post("/auth/login", json={"email": email, "password": pw})


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_login_ok():
    r = login("student@th-deg.de", "test123")
    assert r.status_code == 200
    assert r.json()["role"] == "student"


def test_login_wrong_password():
    assert login("student@th-deg.de", "nope").status_code == 401


def test_me_needs_token():
    assert client.get("/users/me").status_code == 401


def test_me_returns_user_without_password():
    t = login("student@th-deg.de", "test123").json()["token"]
    body = client.get("/users/me", headers=auth(t)).json()
    assert body["email"] == "student@th-deg.de" and "password" not in body


def test_student_cannot_use_admin_endpoint():
    t = login("student@th-deg.de", "test123").json()["token"]
    assert client.get("/admin/ping", headers=auth(t)).status_code == 403


def test_admin_can_use_admin_endpoint():
    t = login("admin@th-deg.de", "admin123").json()["token"]
    assert client.get("/admin/ping", headers=auth(t)).status_code == 200


def test_export_has_profile():
    t = login("student@th-deg.de", "test123").json()["token"]
    assert "profile" in client.get("/users/me/export", headers=auth(t)).json()
