import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_activity_list():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    response = client.post(
        "/activities/Chess Club/signup?email=teststudent@mergington.edu"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up teststudent@mergington.edu for Chess Club"
    assert any(
        p.lower() == "teststudent@mergington.edu"
        for p in activities["Chess Club"]["participants"]
    )


def test_signup_duplicate_participant_returns_400():
    response = client.post(
        "/activities/Chess Club/signup?email=michael@mergington.edu"
    )

    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_remove_participant_from_activity():
    response = client.delete(
        "/activities/Chess Club/participants?email=michael@mergington.edu"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"
    assert all(
        p.lower() != "michael@mergington.edu"
        for p in activities["Chess Club"]["participants"]
    )


def test_remove_nonexistent_participant_returns_404():
    response = client.delete(
        "/activities/Chess Club/participants?email=notregistered@mergington.edu"
    )

    assert response.status_code == 404
    assert "is not signed up" in response.json()["detail"]
