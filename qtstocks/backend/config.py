import os
import json
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def load_google_credentials():
    try:
        credentials_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
        if os.path.exists(credentials_path):
            with open(credentials_path, 'r') as f:
                credentials = json.load(f)
                return credentials['web']
        else:
            print("Warning: credentials.json not found")
            return {
                'client_id': os.getenv('GOOGLE_CLIENT_ID'),
                'client_secret': os.getenv('GOOGLE_CLIENT_SECRET')
            }
    except Exception as e:
        print(f"Error loading Google credentials: {e}")
        return {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'client_secret': os.getenv('GOOGLE_CLIENT_SECRET')
        }

class Config:
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-please-change-in-production')
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable is not set")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    SESSION_COOKIE_SECURE = False  # Set to True in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = None  # Changed from 'Lax' to None to allow cross-site requests
    SESSION_COOKIE_DOMAIN = None  # Allow cookies for all domains
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # Admin user configuration
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    # Google OAuth2 settings
    google_creds = load_google_credentials()
    GOOGLE_CLIENT_ID = google_creds['client_id']
    GOOGLE_CLIENT_SECRET = google_creds['client_secret']
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration" 