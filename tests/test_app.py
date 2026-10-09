import pytest
from fastapi.testclient import TestClient

from src import app as app_module


TEST_ACTIVITY = "Chess Club"
TEST_PARTICIPANT = "new.student@mergington.edu"


@pytest.fixture
def activity_data(monkeypatch):
    activities = {
        TEST_ACTIVITY: {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 5,
            "participants": ["existing.student@mergington.edu"],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return activities


@pytest.fixture
def client(activity_data):
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_data(client, activity_data):
    # Arrange
    expected_activities = activity_data.copy()

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client, activity_data):
    # Arrange
    expected_participants = activity_data[TEST_ACTIVITY]["participants"] + [TEST_PARTICIPANT]

    # Act
    response = client.post(
        f"/activities/{TEST_ACTIVITY}/signup",
        params={"email": TEST_PARTICIPANT},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {TEST_PARTICIPANT} for {TEST_ACTIVITY}"}
    assert activity_data[TEST_ACTIVITY]["participants"] == expected_participants


def test_signup_rejects_duplicate_participant(client, activity_data):
    # Arrange
    participant = activity_data[TEST_ACTIVITY]["participants"][0]
    original_participants = activity_data[TEST_ACTIVITY]["participants"].copy()

    # Act
    response = client.post(
        f"/activities/{TEST_ACTIVITY}/signup",
        params={"email": participant},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}
    assert activity_data[TEST_ACTIVITY]["participants"] == original_participants


def test_signup_rejects_unknown_activity(client):
    # Arrange
    unknown_activity = "Unknown Club"

    # Act
    response = client.post(
        f"/activities/{unknown_activity}/signup",
        params={"email": TEST_PARTICIPANT},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client, activity_data):
    # Arrange
    participant = activity_data[TEST_ACTIVITY]["participants"][0]

    # Act
    response = client.delete(
        f"/activities/{TEST_ACTIVITY}/signup",
        params={"email": participant},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {participant} from {TEST_ACTIVITY}"}
    assert participant not in activity_data[TEST_ACTIVITY]["participants"]


def test_unregister_rejects_missing_participant(client, activity_data):
    # Arrange
    original_participants = activity_data[TEST_ACTIVITY]["participants"].copy()

    # Act
    response = client.delete(
        f"/activities/{TEST_ACTIVITY}/signup",
        params={"email": TEST_PARTICIPANT},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}
    assert activity_data[TEST_ACTIVITY]["participants"] == original_participants


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    unknown_activity = "Unknown Club"

    # Act
    response = client.delete(
        f"/activities/{unknown_activity}/signup",
        params={"email": TEST_PARTICIPANT},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}