from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


def setup_activity_state():
    return deepcopy({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        },
        "Soccer Team": {
            "description": "Develop soccer skills and compete in school matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": [],
        },
    })


def test_get_activities_returns_all_activity_data():
    # Arrange
    original = setup_activity_state()
    activities.clear()
    activities.update(original)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "Soccer Team" in payload
    assert payload["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_for_activity_registers_new_participant():
    # Arrange
    original = setup_activity_state()
    activities.clear()
    activities.update(original)
    activity_name = "Soccer Team"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participant():
    # Arrange
    original = setup_activity_state()
    activities.clear()
    activities.update(original)
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities[activity_name]["participants"].count(email) == 1


def test_unregister_participant_removes_email_from_activity():
    # Arrange
    original = setup_activity_state()
    activities.clear()
    activities.update(original)
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Removed {email} from {activity_name}"


def test_unregister_rejects_email_not_in_activity():
    # Arrange
    original = setup_activity_state()
    activities.clear()
    activities.update(original)
    activity_name = "Soccer Team"
    email = "not-signed-up@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"
