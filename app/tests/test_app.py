"""
Unit Tests for Flask Application

This test suite provides comprehensive unit testing for the Flask web application
using pytest framework with SQLite in-memory database for fast, isolated testing.

Test Categories:
- Health endpoint testing (application and database connectivity)
- User management API testing (CRUD operations)
- Database model testing (User and HealthCheck models)
- Error handling and edge cases
- Integration workflow testing

Database Strategy:
- Uses SQLite in-memory database for unit tests (fast, isolated)
- Each test gets a fresh database instance via fixtures
- Tests database models, relationships, and constraints
- Validates JSON serialization and API responses

CircleCI Integration:
- Generates JUnit XML output for native CircleCI test result parsing
- Produces coverage reports (HTML and XML formats)
- Test results automatically collected and displayed in CircleCI UI
- Coverage threshold enforced at 70% minimum

Test Fixtures:
- client: Flask test client with SQLite database
- app_context: Application context for database operations  
- sample_user: Pre-created user for testing
- multiple_users: Multiple users for list/query testing
"""

import json
import pytest
from app import app, db
from models import User, HealthCheck

# pytest markers for better test organization and JUnit XML categorization


@pytest.mark.unit
@pytest.mark.api
class TestHealthEndpoints:
    """
    Test health check endpoints
    
    These tests validate the application health monitoring system:
    - Main health endpoint (/health) 
    - API health endpoint (/api/health)
    - Database connectivity verification
    - Health check record creation
    """
    
    @pytest.mark.database
    def test_health_endpoint(self, client):
        """
        Test the main health endpoint
        
        Validates:
        - HTTP 200 response
        - JSON response format
        - Required fields: status, timestamp, database, version
        - Database connectivity confirmation
        - Health check record creation in database
        """
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert data['database'] == 'connected'
        assert data['version'] == '1.0.0'
    
    def test_api_health_endpoint(self, client):
        """Test the API health endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['database'] == 'connected'
        assert 'user_count' in data
        assert 'timestamp' in data
    
    def test_health_check_creates_record(self, client):
        """Test that health check creates a database record"""
        with app.app_context():
            initial_count = HealthCheck.query.count()
            
        response = client.get('/health')
        assert response.status_code == 200
        
        with app.app_context():
            final_count = HealthCheck.query.count()
            assert final_count == initial_count + 1


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.database
class TestUserEndpoints:
    """Test user management endpoints"""
    
    def test_get_users_empty(self, client):
        """Test getting users when none exist"""
        response = client.get('/api/users')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_create_user(self, client):
        """Test creating a new user"""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com'
        }
        
        response = client.post('/api/users', 
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        
        data = json.loads(response.data)
        assert data['username'] == user_data['username']
        assert data['email'] == user_data['email']
        assert 'id' in data
        assert 'created_at' in data
    
    def test_create_user_missing_data(self, client):
        """Test creating a user with missing data"""
        incomplete_data = {'username': 'onlyusername'}
        
        response = client.post('/api/users',
                             data=json.dumps(incomplete_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'required' in data['error'].lower()
    
    def test_create_duplicate_user(self, client, sample_user):
        """Test creating a user with duplicate username or email"""
        duplicate_data = {
            'username': sample_user['username'],
            'email': 'different@example.com'
        }
        
        response = client.post('/api/users',
                             data=json.dumps(duplicate_data),
                             content_type='application/json')
        
        assert response.status_code == 409
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'already exists' in data['error']
    
    def test_get_users_with_data(self, client, multiple_users):
        """Test getting users when they exist"""
        response = client.get('/api/users')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 3
        
        # Check that users are ordered by created_at desc
        usernames = [user['username'] for user in data]
        assert 'user1' in usernames
        assert 'user2' in usernames
        assert 'user3' in usernames
    
    def test_delete_user(self, client, sample_user):
        """Test deleting a user"""
        user_id = sample_user['id']
        
        response = client.delete(f'/api/users/{user_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'message' in data
        assert 'deleted successfully' in data['message']
        
        # Verify user is actually deleted
        get_response = client.get('/api/users')
        users_data = json.loads(get_response.data)
        user_ids = [user['id'] for user in users_data]
        assert user_id not in user_ids
    
    def test_delete_nonexistent_user(self, client):
        """Test deleting a user that doesn't exist"""
        response = client.delete('/api/users/99999')
        assert response.status_code == 404


@pytest.mark.unit
@pytest.mark.database
class TestDatabaseOperations:
    """Test database-related operations"""
    
    def test_database_init(self, client):
        """Test database initialization endpoint"""
        response = client.get('/api/database/init')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'message' in data
        assert 'initialized successfully' in data['message']
    
    def test_user_model_to_dict(self, client):
        """Test User model to_dict method"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            db.session.add(user)
            db.session.commit()
            
            user_dict = user.to_dict()
            assert user_dict['username'] == 'testuser'
            assert user_dict['email'] == 'test@example.com'
            assert 'id' in user_dict
            assert 'created_at' in user_dict
    
    def test_health_check_model_to_dict(self, client):
        """Test HealthCheck model to_dict method"""
        with app.app_context():
            health_check = HealthCheck(status='healthy')
            db.session.add(health_check)
            db.session.commit()
            
            health_dict = health_check.to_dict()
            assert health_dict['status'] == 'healthy'
            assert 'id' in health_dict
            assert 'timestamp' in health_dict


@pytest.mark.unit
@pytest.mark.api
class TestMainRoutes:
    """Test main application routes"""
    
    def test_index_route(self, client):
        """Test the main index route"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'CircleCI Demo POC' in response.data
        assert b'Application Status' in response.data
    
    def test_404_error_handler(self, client):
        """Test 404 error handling"""
        response = client.get('/nonexistent-endpoint')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['error'] == 'Not found'


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.api
class TestIntegration:
    """Integration tests"""
    
    def test_full_user_workflow(self, client):
        """Test complete user creation and retrieval workflow"""
        # Create a user
        user_data = {
            'username': 'workflowuser',
            'email': 'workflow@example.com'
        }
        
        create_response = client.post('/api/users',
                                    data=json.dumps(user_data),
                                    content_type='application/json')
        assert create_response.status_code == 201
        
        created_user = json.loads(create_response.data)
        user_id = created_user['id']
        
        # Retrieve all users and verify our user is there
        get_response = client.get('/api/users')
        assert get_response.status_code == 200
        
        users = json.loads(get_response.data)
        assert len(users) == 1
        assert users[0]['username'] == user_data['username']
        
        # Delete the user
        delete_response = client.delete(f'/api/users/{user_id}')
        assert delete_response.status_code == 200
        
        # Verify user is gone
        final_get_response = client.get('/api/users')
        final_users = json.loads(final_get_response.data)
        assert len(final_users) == 0
    
    def test_health_and_user_count_consistency(self, client, multiple_users):
        """Test that health endpoint reports correct user count"""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['user_count'] == 3  # Should match the number of users created
        
        # Create another user and check again
        new_user_data = {
            'username': 'healthuser',
            'email': 'health@example.com'
        }
        
        client.post('/api/users',
                   data=json.dumps(new_user_data),
                   content_type='application/json')
        
        health_response = client.get('/api/health')
        health_data = json.loads(health_response.data)
        assert health_data['user_count'] == 4
