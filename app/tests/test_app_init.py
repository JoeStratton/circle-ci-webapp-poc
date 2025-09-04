"""
Tests for Application Initialization and Configuration

This module tests the application initialization functions and configuration
that are not easily testable in the main test suite.
"""

import os
import tempfile
import pytest
from unittest.mock import patch, mock_open
from app import app, init_db, run_init_sql, create_app
from config import get_config


@pytest.mark.unit
class TestAppInitialization:
    """Test application initialization functions"""
    
    def test_init_db_success(self):
        """Test init_db function with successful database creation"""
        with app.app_context():
            # This should work without errors
            init_db()
            # Verify tables were created
            from sqlalchemy import inspect
            inspector = inspect(app.db.engine)
            tables = inspector.get_table_names()
            assert 'users' in tables
            assert 'health_checks' in tables
    
    def test_init_db_with_sql_file(self):
        """Test init_db function when init-db.sql file exists"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            f.write("INSERT INTO user (username, email) VALUES ('test', 'test@example.com');")
            sql_file_path = f.name
        
        try:
            with patch('os.path.exists', return_value=True):
                with patch('os.path.join', return_value=sql_file_path):
                    with patch('app.run_init_sql') as mock_run_init_sql:
                        with app.app_context():
                            init_db()
                            mock_run_init_sql.assert_called_once_with(sql_file_path)
        finally:
            os.unlink(sql_file_path)
    
    def test_init_db_without_sql_file(self):
        """Test init_db function when init-db.sql file doesn't exist"""
        with patch('os.path.exists', return_value=False):
            with patch('app.logger') as mock_logger:
                with app.app_context():
                    init_db()
                    mock_logger.info.assert_called_with("No init-db.sql found, skipping initial data setup")
    
    def test_init_db_exception_handling(self):
        """Test init_db function handles exceptions gracefully"""
        with patch('app.db.create_all', side_effect=Exception("Database error")):
            with patch('app.logger') as mock_logger:
                with app.app_context():
                    init_db()
                    mock_logger.warning.assert_called()
                    mock_logger.info.assert_called_with("Continuing with existing database state")
    
    def test_run_init_sql_success(self):
        """Test run_init_sql function with successful SQL execution"""
        sql_content = "SELECT 1; SELECT 2;"
        
        with patch('builtins.open', mock_open(read_data=sql_content)):
            with patch('app.db.session.execute') as mock_execute:
                with patch('app.db.session.commit') as mock_commit:
                    with patch('app.logger') as mock_logger:
                        with app.app_context():
                            run_init_sql('dummy_path')
                            
                            # Should execute both SQL commands
                            assert mock_execute.call_count == 2
                            mock_commit.assert_called_once()
                            mock_logger.info.assert_called()
    
    def test_run_init_sql_exception_handling(self):
        """Test run_init_sql function handles exceptions gracefully"""
        with patch('builtins.open', side_effect=Exception("File error")):
            with patch('app.logger') as mock_logger:
                with patch('app.db.session.rollback') as mock_rollback:
                    with app.app_context():
                        run_init_sql('dummy_path')
                        mock_logger.warning.assert_called()
                        mock_rollback.assert_called_once()
    
    def test_create_app_function(self):
        """Test create_app function returns proper app instance"""
        app_instance = create_app()
        assert app_instance is not None
        assert hasattr(app_instance, 'config')
        assert hasattr(app_instance, 'db')
    
    def test_create_app_with_context(self):
        """Test create_app function initializes database in context"""
        with patch('app.init_db') as mock_init_db:
            app_instance = create_app()
            mock_init_db.assert_called_once()
            assert app_instance is not None


@pytest.mark.unit
class TestConfiguration:
    """Test configuration loading and environment handling"""
    
    def test_get_config_development(self):
        """Test configuration loading in development mode"""
        with patch.dict(os.environ, {'FLASK_ENV': 'development'}):
            config = get_config()
            assert config['DEBUG'] is True
            assert 'SQLALCHEMY_DATABASE_URI' in config
    
    def test_get_config_production(self):
        """Test configuration loading in production mode"""
        with patch.dict(os.environ, {'FLASK_ENV': 'production'}):
            config = get_config()
            assert config['DEBUG'] is False
            assert 'SQLALCHEMY_DATABASE_URI' in config
    
    def test_get_config_testing(self):
        """Test configuration loading in testing mode"""
        with patch.dict(os.environ, {'FLASK_ENV': 'testing'}):
            config = get_config()
            assert config['TESTING'] is True
            assert 'SQLALCHEMY_DATABASE_URI' in config
    
    def test_get_config_with_database_url(self):
        """Test configuration loading with custom DATABASE_URL"""
        test_db_url = 'postgresql://user:pass@localhost/testdb'
        with patch.dict(os.environ, {'DATABASE_URL': test_db_url, 'FLASK_ENV': 'production'}):
            config = get_config()
            assert config['SQLALCHEMY_DATABASE_URI'] == test_db_url
    
    def test_get_config_with_port(self):
        """Test configuration loading with custom PORT"""
        with patch.dict(os.environ, {'PORT': '8080'}):
            config = get_config()
            assert config['PORT'] == 8080


@pytest.mark.unit
class TestErrorHandlers:
    """Test error handler functions"""
    
    def test_404_error_handler(self):
        """Test 404 error handler"""
        from app import not_found
        response, status_code = not_found(None)
        assert status_code == 404
        assert response['error'] == 'Not found'
    
    def test_500_error_handler(self):
        """Test 500 error handler"""
        from app import internal_error
        with patch('app.db.session.rollback') as mock_rollback:
            response, status_code = internal_error(None)
            assert status_code == 500
            assert response['error'] == 'Internal server error'
            mock_rollback.assert_called_once()


@pytest.mark.unit
class TestMainExecution:
    """Test main execution block"""
    
    def test_main_execution_config_loading(self):
        """Test that main execution loads config correctly"""
        # This tests the config loading in the main execution block
        assert hasattr(app, 'config')
        assert 'SQLALCHEMY_DATABASE_URI' in app.config
    
    def test_main_execution_with_context(self):
        """Test main execution with app context"""
        with app.app_context():
            # Test that database operations work in context
            from sqlalchemy import text
            result = app.db.session.execute(text('SELECT 1')).fetchone()
            assert result[0] == 1
