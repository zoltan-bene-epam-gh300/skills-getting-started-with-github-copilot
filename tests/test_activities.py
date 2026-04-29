"""Tests for the FastAPI activities management endpoints."""

import pytest


class TestGetActivities:
    """Test suite for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, test_client):
        """Test that GET /activities returns all activities."""
        response = test_client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_returns_correct_structure(self, test_client):
        """Test that each activity has the correct data structure."""
        response = test_client.get("/activities")
        data = response.json()
        
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_get_activities_shows_initial_participants(self, test_client):
        """Test that activities show their initial participants."""
        response = test_client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_participant_success(self, test_client):
        """Test successful signup of a new participant."""
        response = test_client.post(
            "/activities/Chess Club/signup",
            params={"email": "john@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "john@mergington.edu" in data["message"]

    def test_signup_adds_participant_to_activity(self, test_client):
        """Test that signup adds participant to the activity's participant list."""
        test_client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        response = test_client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        assert "newstudent@mergington.edu" in chess_club["participants"]
        assert len(chess_club["participants"]) == 3

    def test_signup_duplicate_registration_fails(self, test_client):
        """Test that signing up twice for the same activity returns 400 error."""
        email = "michael@mergington.edu"
        
        response = test_client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_nonexistent_activity_fails(self, test_client):
        """Test that signup to non-existent activity returns 404 error."""
        response = test_client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_signup_multiple_different_activities(self, test_client):
        """Test that a student can sign up for multiple different activities."""
        email = "versatile@mergington.edu"
        
        response1 = test_client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        response2 = test_client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        activities_response = test_client.get("/activities")
        data = activities_response.json()
        
        assert email in data["Chess Club"]["participants"]
        assert email in data["Programming Class"]["participants"]


class TestUnregisterFromActivity:
    """Test suite for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_participant_success(self, test_client):
        """Test successful unregistration of a participant."""
        response = test_client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_removes_participant_from_activity(self, test_client):
        """Test that unregister removes participant from activity's list."""
        test_client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        
        response = test_client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        assert "michael@mergington.edu" not in chess_club["participants"]
        assert len(chess_club["participants"]) == 1
        assert "daniel@mergington.edu" in chess_club["participants"]

    def test_unregister_not_registered_participant_fails(self, test_client):
        """Test that unregistering a non-registered participant returns 400 error."""
        response = test_client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"].lower()

    def test_unregister_nonexistent_activity_fails(self, test_client):
        """Test that unregister from non-existent activity returns 404 error."""
        response = test_client.delete(
            "/activities/Nonexistent Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_unregister_then_register_again(self, test_client):
        """Test that a participant can unregister and then register again."""
        email = "michael@mergington.edu"
        
        # Unregister
        response1 = test_client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Re-register
        response2 = test_client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify registered
        activities_response = test_client.get("/activities")
        data = activities_response.json()
        assert email in data["Chess Club"]["participants"]


class TestRootRedirect:
    """Test suite for GET / endpoint."""

    def test_root_redirects_to_index(self, test_client):
        """Test that GET / redirects to /static/index.html."""
        response = test_client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
