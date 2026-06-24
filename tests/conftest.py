"""
Pytest configuration and shared fixtures for the test suite.
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Fixture that provides a FastAPI test client.
    
    Arrange: Create the test client
    This allows tests to make requests to the app without running a live server.
    """
    return TestClient(app)
