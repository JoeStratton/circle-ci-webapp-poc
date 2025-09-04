"""
Routes for the CircleCI Demo Application

This module contains all Flask routes for the application.
For a POC, we keep all routes in one file for simplicity.

Routes included:
- Main web interface (/)
- Health check endpoints (/health, /api/health)
- User management API (/api/users)
- Database management (/api/database/init)
"""

import os
import logging
from datetime import datetime
from flask import Blueprint, render_template, jsonify, request, current_app
from sqlalchemy import text
from models import User, HealthCheck

# =============================================================================
# ROUTE SETUP
# =============================================================================

# Create blueprint for all routes
bp = Blueprint('main', __name__)

# Get logger for this module
logger = logging.getLogger(__name__)

# Global flag for database initialization (lazy initialization for Gunicorn)
_db_initialized = False


def ensure_db_initialized():
    """
    Ensure database is initialized (lazy initialization for Gunicorn)
    
    This function implements lazy database initialization to avoid
    application context issues when running with Gunicorn. It only
    initializes the database once per worker process.
    """
    global _db_initialized
    if not _db_initialized:
        try:
            from app import init_db
            init_db()
            _db_initialized = True
            logger.info("Database initialized on first request")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")


# =============================================================================
# MAIN WEB INTERFACE ROUTES
# =============================================================================

@bp.route('/')
def index():
    """
    Main application page with user interface
    
    This route serves the main web interface with:
    - Application status information
    - Database connectivity status
    - User management interface
    - Recent users display
    """
    ensure_db_initialized()
    
    # Test database connection
    try:
        current_app.db.session.execute(text('SELECT 1'))
        db_status = 'Connected'
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        db_status = 'Disconnected'
    
    # Get recent users
    try:
        users = User.query.order_by(User.created_at.desc()).limit(5).all()
        user_list = [user.to_dict() for user in users]
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        user_list = []
    
    return render_template(
        'index.html',
        status='Running',
        db_status=db_status,
        environment=os.environ.get('ENVIRONMENT', 'development'),
        users=user_list
    )


# =============================================================================
# HEALTH CHECK ROUTES
# =============================================================================

@bp.route('/health')
def health_check():
    """
    Health check endpoint for load balancers
    
    This endpoint provides basic health status for load balancers
    and monitoring systems. It tests database connectivity and
    records the health check request.
    """
    ensure_db_initialized()
    
    try:
        current_app.db.session.execute(text('SELECT 1'))
        
        # Record health check
        health_record = HealthCheck(status='healthy')
        current_app.db.session.add(health_record)
        current_app.db.session.commit()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': health_record.timestamp.isoformat(),
            'database': 'connected',
            'version': '1.0.0'
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@bp.route('/api/health')
def api_health():
    """
    API health check with database test
    
    This endpoint provides detailed health information including
    database connectivity and user count statistics.
    """
    ensure_db_initialized()
    
    try:
        result = current_app.db.session.execute(text('SELECT COUNT(*) as count FROM users')).fetchone()
        user_count = result.count if result else 0
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'user_count': user_count,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"API health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


# =============================================================================
# USER MANAGEMENT API ROUTES
# =============================================================================

@bp.route('/api/users', methods=['GET'])
def get_users():
    """
    Get all users
    
    This endpoint retrieves all users from the database and returns
    them as a JSON array with user information.
    """
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        return jsonify([user.to_dict() for user in users])
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/api/users', methods=['POST'])
def create_user():
    """
    Create a new user
    
    This endpoint creates a new user with the provided username and email.
    It validates that the user doesn't already exist before creating.
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('email'):
            return jsonify({'error': 'Username and email are required'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == data['username']) | (User.email == data['email'])
        ).first()
        
        if existing_user:
            return jsonify({
                'error': 'User with this username or email already exists'
            }), 409
        
        # Create new user
        user = User(username=data['username'], email=data['email'])
        current_app.db.session.add(user)
        current_app.db.session.commit()
        
        logger.info(f"Created user: {user.username}")
        return jsonify(user.to_dict()), 201
        
    except Exception as e:
        current_app.db.session.rollback()
        logger.error(f"Error creating user: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Delete a user
    
    This endpoint deletes a user by their ID.
    """
    try:
        user = User.query.get_or_404(user_id)
        current_app.db.session.delete(user)
        current_app.db.session.commit()
        
        logger.info(f"Deleted user: {user.username}")
        return jsonify({'message': 'User deleted successfully'})
        
    except Exception as e:
        current_app.db.session.rollback()
        logger.error(f"Error deleting user: {e}")
        return jsonify({'error': str(e)}), 500


# =============================================================================
# DATABASE MANAGEMENT ROUTES
# =============================================================================

@bp.route('/api/database/init')
def init_database():
    """
    Initialize database tables
    
    This endpoint manually initializes the database tables.
    Useful for development and testing purposes.
    """
    try:
        current_app.db.create_all()
        return jsonify({'message': 'Database initialized successfully'})
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return jsonify({'error': str(e)}), 500
