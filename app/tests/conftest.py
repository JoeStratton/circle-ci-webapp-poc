"""
Test Configuration and Fixtures for pytest Framework

pytest: Python testing framework that makes it easy to write simple and scalable tests
Key Features Used:
- Fixtures: Reusable test setup and teardown (@pytest.fixture)
- Markers: Test categorization and selection (@pytest.mark.unit, @pytest.mark.integration)
- Parameterization: Running tests with different inputs
- Coverage Integration: Code coverage reporting with pytest-cov
- JUnit XML Output: Native CircleCI integration with --junit-xml
- Assertions: Simple assert statements for test validation

Framework Benefits:
- Simple test writing with minimal boilerplate
- Powerful fixture system for test isolation
- Excellent error reporting and debugging
- Plugin ecosystem (coverage, xdist, mock, etc.)
- Native JUnit XML support for CI/CD integration
"""

import os
import pytest
import tempfile
from app import app, db
from models import User, HealthCheck


@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    # Use in-memory SQLite for testing
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def app_context():
    """Create an application context for testing"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def sample_user(client):
    """Create a sample user for testing"""
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com'
    }
    
    with app.app_context():
        user = User(**user_data)
        db.session.add(user)
        db.session.commit()
        # Return user data instead of the object to avoid detached instance issues
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }


@pytest.fixture
def multiple_users(client):
    """Create multiple users for testing"""
    users_data = [
        {'username': 'user1', 'email': 'user1@example.com'},
        {'username': 'user2', 'email': 'user2@example.com'},
        {'username': 'user3', 'email': 'user3@example.com'}
    ]
    
    users = []
    with app.app_context():
        for user_data in users_data:
            user = User(**user_data)
            db.session.add(user)
            users.append({
                'id': user.id,
                'username': user.username,
                'email': user.email
            })
        db.session.commit()
        return users
