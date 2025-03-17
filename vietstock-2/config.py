import os

class Config:
    # Flask configuration
    SECRET_KEY = os.urandom(32)  # Generate a secure random key
    
    # CSRF configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.urandom(32)
    WTF_CSRF_TIME_LIMIT = None  # No time limit for CSRF tokens
    
    # Session configuration
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = False  # Allow HTTP in development
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'Lax'

    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'postgresql://qtstock:qtstock123@localhost:5432/qtstock'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # User configuration
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin123'  # Change this in production 