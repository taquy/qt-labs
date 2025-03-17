import os

class Config:
    # Flask configuration
    SECRET_KEY = 'your-secret-key-here'
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = 'csrf-secret-key'

    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'postgresql://vietstock:vietstock123@localhost:5432/vietstock'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # User configuration
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin123'  # Change this in production 