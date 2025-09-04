"""
Flask Web Application for CircleCI Field Engineer Demo

This is a simplified POC application demonstrating:
- PostgreSQL database integration via sidecar container
- Health monitoring and API endpoints
- User management with CRUD operations
- Dark mode UI with persistence
- Docker containerization

Architecture:
- Main container: Flask app
- Sidecar container: PostgreSQL database
- Both containers run in same ECS task

For simplicity, this POC keeps related functionality together in single files.
"""

import os
import logging
from flask import Flask
# SQLAlchemy is imported via models.py as 'db'
from flask_migrate import Migrate
from config import get_config
from routes import bp
from models import db

# =============================================================================
# APPLICATION SETUP
# =============================================================================

# Configure logging for the application
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)

# Load configuration from environment variables
config = get_config()
app.config.update(config)

# Initialize database connection
db.init_app(app)
migrate = Migrate(app, db)

# Make database available globally for easy access
app.db = db

# Database is now properly initialized in models.py

# Register all routes from the routes module
app.register_blueprint(bp)

# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================


def init_db():
    """
    Initialize the database with tables and initial data

    This function:
    - Creates all database tables defined by SQLAlchemy models
    - Runs initial data setup from init-db.sql if available
    - Handles errors gracefully for cases where tables already exist
    - Used for both development and production environments
    """
    try:
        # Create all tables defined by models (won't fail if tables exist)
        db.create_all()
        logger.info("Database tables created/verified successfully")

        # Run initial data setup if init-db.sql exists
        init_sql_path = os.path.join(os.path.dirname(__file__), 'init-db.sql')
        if os.path.exists(init_sql_path):
            run_init_sql(init_sql_path)
        else:
            logger.info("No init-db.sql found, skipping initial data setup")

    except Exception as e:
        # Log the error but don't raise it - let the app continue
        # This handles cases where tables already exist or other DB issues
        logger.warning(f"Database initialization warning: {e}")
        logger.info("Continuing with existing database state")


def run_init_sql(sql_file_path):
    """
    Execute SQL commands from init-db.sql file

    This function:
    - Reads SQL commands from the initialization file
    - Executes them using SQLAlchemy connection
    - Handles PostgreSQL-specific commands
    - Provides error handling for SQL execution
    """
    try:
        with open(sql_file_path, 'r') as f:
            sql_content = f.read()

        # Split SQL commands by semicolon and execute each
        sql_commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]

        for command in sql_commands:
            if command:
                db.session.execute(db.text(command))

        db.session.commit()
        logger.info(f"Successfully executed SQL from {sql_file_path}")

    except Exception as e:
        logger.warning(f"Failed to execute init SQL: {e}")
        db.session.rollback()


# =============================================================================
# ERROR HANDLERS
# =============================================================================


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors - page not found"""
    return {'error': 'Not found'}, 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors - internal server error"""
    db.session.rollback()
    return {'error': 'Internal server error'}, 500


# =============================================================================
# APPLICATION FACTORY & EXECUTION
# =============================================================================


def create_app():
    """
    Application factory pattern for gunicorn compatibility

    This function creates and configures the Flask application.
    Used by Gunicorn to initialize the app in production.
    """
    with app.app_context():
        init_db()
    return app


# For direct execution (development/testing)
if __name__ == '__main__':
    # Initialize database for direct execution
    with app.app_context():
        init_db()

    # Run the application
    port = config.PORT
    debug = config.DEBUG

    logger.info(f"Starting Flask application on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
