"""
Database models for the CircleCI Demo Application

This module contains all SQLAlchemy models for the application.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Database instance - will be set by main app
db = SQLAlchemy()


class User(db.Model):
    """
    User model for storing application users
    
    Simple model with basic user information and automatic timestamps.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON responses"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class HealthCheck(db.Model):
    """
    Health check model for monitoring database connectivity
    
    Tracks health check requests for monitoring and validation.
    """
    __tablename__ = 'health_checks'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='healthy')
    
    def to_dict(self):
        """Convert to dictionary for JSON responses"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'status': self.status
        }
    
    def __repr__(self):
        return f'<HealthCheck {self.status} at {self.timestamp}>'
