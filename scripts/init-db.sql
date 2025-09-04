-- Database initialization script for PostgreSQL sidecar container
-- This script runs automatically when the Flask application starts up
-- It creates initial sample data for development and testing

-- Note: Tables are created by SQLAlchemy models, not by this script
-- This script only inserts initial data

-- Insert sample data for development (only if not exists)
INSERT INTO users (username, email) 
SELECT 'admin', 'admin@example.com'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin');

INSERT INTO users (username, email) 
SELECT 'demo', 'demo@example.com'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'demo');

-- Insert initial health check record
INSERT INTO health_checks (status) VALUES ('healthy');

-- Create indexes for performance (PostgreSQL compatible)
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_health_checks_timestamp ON health_checks(timestamp);
