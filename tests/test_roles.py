from tests.conftest import auth


def test_student_cannot_use_admin_endpoint(client):
    assert client.get("/admin/ping", headers=auth(client)).status_code == 403


def test_admin_can_use_admin_endpoint(client):
    h = auth(client, "admin@th-deg.de", "admin123")
    assert client.get("/admin/ping", headers=h).status_code == 200
