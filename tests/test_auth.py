from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_register_duplicate_username():
    client.post("/auth/register", json={"username": "duplicate", "email": "d1@example.com", "password": "pass"})
    response = client.post("/auth/register", json={"username": "duplicate", "email": "d2@example.com", "password": "pass"})
    assert response.status_code == 400


def test_login_invalid_credentials():
    client.post("/auth/register", json={"username": "user", "email": "u@example.com", "password": "correct"})
    response = client.post("/auth/token", data={"username": "user", "password": "wrong"})
    assert response.status_code == 401


def test_protected_route_invalid_token():
    response = client.get("/tasks", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401


def test_protected_route_no_token():
    response = client.get("/tasks")
    assert response.status_code == 401
