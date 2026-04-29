"""Pytest configuration and fixtures for API tests."""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def test_activities():
    """Fixture that provides a fresh copy of activities for each test."""
    return deepcopy(activities)


@pytest.fixture
def test_client(test_activities):
    """Fixture that provides a TestClient with test app and fresh activities."""
    # Replace the app's activities with test data
    import src.app
    original_activities = src.app.activities.copy()
    src.app.activities.clear()
    src.app.activities.update(test_activities)
    
    client = TestClient(app)
    
    yield client
    
    # Restore original activities after test
    src.app.activities.clear()
    src.app.activities.update(original_activities)
