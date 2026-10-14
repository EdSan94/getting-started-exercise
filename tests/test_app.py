import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    test_activities = {
        "Test Activity": {
            "description": "An activity for API tests",
            "schedule": "Mondays, 3:00 PM - 4:00 PM",
            "max_participants": 2,
            "participants": ["existing@example.com"],
        }
    }
    monkeypatch.setattr(app_module, "activities", test_activities)
    return TestClient(app_module.app, follow_redirects=False)


def test_root_redirects_to_activity_page(client):
    response = client.get("/")

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json()["Test Activity"]["participants"] == ["existing@example.com"]


def test_signup_adds_participant(client):
    response = client.post(
        "/activities/Test Activity/signup",
        params={"email": "new@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up new@example.com for Test Activity"}
    assert "new@example.com" in client.get("/activities").json()["Test Activity"]["participants"]


def test_signup_returns_404_for_unknown_activity(client):
    response = client.post(
        "/activities/Unknown/signup",
        params={"email": "new@example.com"},
    )

    assert response.status_code == 404


def test_signup_rejects_duplicate_participant(client):
    response = client.post(
        "/activities/Test Activity/signup",
        params={"email": "existing@example.com"},
    )

    assert response.status_code == 400
    assert client.get("/activities").json()["Test Activity"]["participants"] == [
        "existing@example.com"
    ]


def test_unregister_removes_participant(client):
    response = client.delete(
        "/activities/Test Activity/signup",
        params={"email": "existing@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Removed existing@example.com from Test Activity"}
    assert client.get("/activities").json()["Test Activity"]["participants"] == []


def test_unregister_returns_404_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown/signup",
        params={"email": "existing@example.com"},
    )

    assert response.status_code == 404


def test_unregister_returns_404_for_unregistered_participant(client):
    response = client.delete(
        "/activities/Test Activity/signup",
        params={"email": "missing@example.com"},
    )

    assert response.status_code == 404