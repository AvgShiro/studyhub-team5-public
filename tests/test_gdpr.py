from app.gdpr_hooks import DELETERS, EXPORTERS, register
from tests.conftest import auth, login


def test_export_includes_registered_teams(client):
    register("demo", exporter=lambda uid: [f"data for {uid}"], deleter=lambda uid: None)
    try:
        body = client.get("/users/me/export", headers=auth(client)).json()
        assert "profile" in body and "demo" in body
    finally:
        EXPORTERS.pop("demo"); DELETERS.pop("demo")


def test_delete_calls_teams_then_removes_user(client):
    seen = []
    register("demo", exporter=lambda uid: [], deleter=seen.append)
    try:
        h = auth(client, "admin@th-deg.de", "admin123")
        assert client.delete("/users/me", headers=h).status_code == 204
        assert seen  # the team's deleter was called with the user id
        assert login(client, "admin@th-deg.de", "admin123").status_code == 401
    finally:
        EXPORTERS.pop("demo"); DELETERS.pop("demo")
