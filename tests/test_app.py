import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)
original_activities = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_activities))
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_activities():
    # Arrange
    expected_description = "Learn strategies and compete in chess tournaments"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == expected_description


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "testuser@mergington.edu"
    signup_url = f"/activities/Chess%20Club/signup?email={email}"

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_for_unknown_activity_returns_404():
    # Arrange
    signup_url = "/activities/Unknown%20Activity/signup?email=testuser@mergington.edu"

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_for_existing_participant_returns_400():
    # Arrange
    email = "michael@mergington.edu"
    signup_url = f"/activities/Chess%20Club/signup?email={email}"

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant_removes_participant():
    # Arrange
    email = "michael@mergington.edu"
    unregister_url = f"/activities/Chess%20Club/participants?email={email}"

    # Act
    response = client.delete(unregister_url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"
    assert email not in app_module.activities["Chess Club"]["participants"]


def test_unregister_missing_participant_returns_404():
    # Arrange
    unregister_url = "/activities/Chess%20Club/participants?email=ghost@mergington.edu"

    # Act
    response = client.delete(unregister_url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
