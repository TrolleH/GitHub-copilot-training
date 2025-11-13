"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Outdoor soccer training, drills and weekend matches",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 22,
            "participants": ["liam@mergington.edu", "noah@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball practices and interschool games",
            "schedule": "Mondays and Thursdays, 5:00 PM - 7:00 PM",
            "max_participants": 15,
            "participants": ["ava@mergington.edu", "isabella@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore drawing, painting, and mixed media projects",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["mia@mergington.edu", "charlotte@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting workshops, rehearsals and school productions",
            "schedule": "Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
        },
        "Debate Team": {
            "description": "Practice public speaking, argumentation and competitive debates",
            "schedule": "Thursdays, 6:00 PM - 7:30 PM",
            "max_participants": 16,
            "participants": ["elijah@mergington.edu", "logan@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments, science fairs and research projects",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["lucas@mergington.edu", "zoe@mergington.edu"]
        }
    }
    
    # Store original state
    original_state = {}
    for key, value in activities.items():
        original_state[key] = value.copy()
    
    yield
    
    # Restore original state after test
    activities.clear()
    for key, value in original_activities.items():
        activities[key] = value.copy()


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint"""
    
    def test_get_all_activities(self, client, reset_activities):
        """Test fetching all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        
    def test_activities_structure(self, client, reset_activities):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignupEndpoint:
    """Tests for the /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant(self, client, reset_activities):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "Signed up" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        updated_activity = activities_response.json()["Chess Club"]
        assert "newstudent@mergington.edu" in updated_activity["participants"]
    
    def test_signup_duplicate_participant(self, client, reset_activities):
        """Test that duplicate signups are rejected"""
        # First signup
        response1 = client.post(
            "/activities/Chess Club/signup?email=test@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Duplicate signup
        response2 = client.post(
            "/activities/Chess Club/signup?email=test@mergington.edu"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup to a nonexistent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_already_exists(self, client, reset_activities):
        """Test signup for already registered participant"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]


class TestUnregisterEndpoint:
    """Tests for the /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_participant(self, client, reset_activities):
        """Test unregistering a participant"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "Unregistered" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        updated_activity = activities_response.json()["Chess Club"]
        assert "michael@mergington.edu" not in updated_activity["participants"]
    
    def test_unregister_nonexistent_participant(self, client, reset_activities):
        """Test unregistering a participant who isn't registered"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_from_nonexistent_activity(self, client, reset_activities):
        """Test unregistering from a nonexistent activity"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_multiple_participants(self, client, reset_activities):
        """Test unregistering multiple participants from the same activity"""
        # Unregister first participant
        response1 = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Unregister second participant
        response2 = client.delete(
            "/activities/Chess Club/unregister?email=daniel@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify both participants were removed
        activities_response = client.get("/activities")
        updated_activity = activities_response.json()["Chess Club"]
        assert len(updated_activity["participants"]) == 0


class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_signup_and_unregister_workflow(self, client, reset_activities):
        """Test complete workflow: signup and unregister"""
        # Signup
        signup_response = client.post(
            "/activities/Art Club/signup?email=newartist@mergington.edu"
        )
        assert signup_response.status_code == 200
        
        # Verify added
        check_response = client.get("/activities")
        activity = check_response.json()["Art Club"]
        assert "newartist@mergington.edu" in activity["participants"]
        initial_count = len(activity["participants"])
        
        # Unregister
        unregister_response = client.delete(
            "/activities/Art Club/unregister?email=newartist@mergington.edu"
        )
        assert unregister_response.status_code == 200
        
        # Verify removed
        final_response = client.get("/activities")
        final_activity = final_response.json()["Art Club"]
        assert "newartist@mergington.edu" not in final_activity["participants"]
        assert len(final_activity["participants"]) == initial_count - 1
    
    def test_multiple_signups_and_unregisters(self, client, reset_activities):
        """Test multiple signups and unregisters"""
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        # Signup all
        for email in emails:
            response = client.post(
                f"/activities/Debate Team/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all added
        check_response = client.get("/activities")
        activity = check_response.json()["Debate Team"]
        for email in emails:
            assert email in activity["participants"]
        
        # Unregister all
        for email in emails:
            response = client.delete(
                f"/activities/Debate Team/unregister?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all removed
        final_response = client.get("/activities")
        final_activity = final_response.json()["Debate Team"]
        for email in emails:
            assert email not in final_activity["participants"]
