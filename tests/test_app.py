"""
Comprehensive test suite for the Mergington High School API.
Uses the AAA (Arrange-Act-Assert) testing pattern.
"""
import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        Test that GET /activities returns all available activities.

        Arrange: Client is ready (from fixture)
        Act: Make GET request to /activities
        Assert: Response status is 200 and contains expected activities
        """
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Debate Team",
            "Swimming Club",
            "Art Studio",
            "Drama Club",
            "Science Club",
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        for activity_name in expected_activities:
            assert activity_name in activities

    def test_get_activities_returns_activity_details(self, client):
        """
        Test that each activity has required fields.

        Arrange: Client is ready
        Act: Make GET request to /activities
        Assert: Each activity has description, schedule, max_participants, and participants
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, details in activities.items():
            assert isinstance(details, dict)
            for field in required_fields:
                assert field in details, f"{activity_name} missing {field}"
            assert isinstance(details["participants"], list)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_adds_participant_to_activity(self, client):
        """
        Test that signing up adds a participant to an activity.

        Arrange: Get initial state and pick an activity
        Act: Sign up a student for an activity
        Assert: Response is successful and participant is added to activity list
        """
        # Arrange
        email = "alice@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

        # Verify participant is in activity list
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]

    def test_signup_with_invalid_activity_returns_404(self, client):
        """
        Test that signing up for a non-existent activity returns 404.

        Arrange: Prepare invalid activity name
        Act: Sign up for activity that doesn't exist
        Assert: Response status is 404 with appropriate error message
        """
        # Arrange
        email = "bob@mergington.edu"
        activity_name = "NonexistentActivity"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_duplicate_email_returns_400(self, client):
        """
        Test that signing up twice with the same email returns 400.

        Arrange: Sign up a student once
        Act: Try to sign up the same student again
        Assert: Response status is 400 indicating already signed up
        """
        # Arrange
        email = "charlie@mergington.edu"
        activity_name = "Programming Class"

        # First signup
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Act - Try to sign up again
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_multiple_different_emails_can_signup(self, client):
        """
        Test that different students can sign up for the same activity.

        Arrange: Prepare two different email addresses
        Act: Sign up both students
        Assert: Both are successfully added to the activity
        """
        # Arrange
        emails = ["diane@mergington.edu", "evan@mergington.edu"]
        activity_name = "Gym Class"

        # Act
        responses = []
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email},
            )
            responses.append(response)

        # Assert
        for response in responses:
            assert response.status_code == 200

        # Verify both are in participants list
        activities = client.get("/activities").json()
        participants = activities[activity_name]["participants"]
        for email in emails:
            assert email in participants


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_removes_participant_from_activity(self, client):
        """
        Test that unregistering removes a participant from an activity.

        Arrange: Sign up a student first
        Act: Unregister that student
        Assert: Response is successful and participant is removed from list
        """
        # Arrange
        email = "frank@mergington.edu"
        activity_name = "Debate Team"

        # Sign up first
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

        # Verify participant is removed
        activities = client.get("/activities").json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_invalid_activity_returns_404(self, client):
        """
        Test that unregistering from non-existent activity returns 404.

        Arrange: Prepare invalid activity name
        Act: Unregister from activity that doesn't exist
        Assert: Response status is 404
        """
        # Arrange
        email = "grace@mergington.edu"
        activity_name = "FakeActivity"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_nonexistent_participant_returns_404(self, client):
        """
        Test that unregistering a participant not in the activity returns 404.

        Arrange: Pick an activity where participant is not signed up
        Act: Try to unregister that participant
        Assert: Response status is 404 with appropriate message
        """
        # Arrange
        email = "henry@mergington.edu"
        activity_name = "Swimming Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_then_can_signup_again(self, client):
        """
        Test that a student can sign up again after unregistering.

        Arrange: Sign up a student
        Act: Unregister, then sign up again
        Assert: Second signup succeeds
        """
        # Arrange
        email = "iris@mergington.edu"
        activity_name = "Art Studio"

        # Sign up first time
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Act - Unregister
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email},
        )

        # Act - Sign up again
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]


class TestRootEndpoint:
    """Tests for the root endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """
        Test that GET / redirects to /static/index.html.

        Arrange: Client is ready
        Act: Make GET request to root path
        Assert: Response is a redirect (status 307) to /static/index.html
        """
        # Arrange - nothing needed

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert "static/index.html" in response.headers["location"]
