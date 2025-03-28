import sys
import os
import pytest
from flask import Flask
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extensions import db
from models import User, UserJWT
from controllers.auth import init_auth_routes
from flask_restx import Api
import jwt as PyJWT

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['GOOGLE_CLIENT_ID'] = 'test_google_client_id'
    
    db.init_app(app)
    
    api = Api(app)
    auth_ns = api.namespace('auth', description='Authentication operations')
    init_auth_routes(app, auth_ns)
    
    with app.app_context():
        db.create_all()
    
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_register(client):
    response = client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'testpassword',
        'name': 'Test User'
    })
    assert response.status_code == 201
    assert 'User registered successfully' in response.json['message']
    assert response.json['user']['email'] == 'test@example.com'
    assert response.json['user']['name'] == 'Test User'

def test_login(client):
    # First, register a user
    client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'testpassword',
        'name': 'Test User'
    })
    
    # Then, try to login
    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'testpassword'
    })
    assert response.status_code == 200
    assert 'token' in response.json
    assert response.json['user']['email'] == 'test@example.com'
    assert response.json['user']['name'] == 'Test User'

def test_login_invalid_credentials(client):
    response = client.post('/auth/login', json={
        'email': 'nonexistent@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert 'Invalid email or password' in response.json['message']

@patch('google.oauth2.id_token.verify_oauth2_token')
@patch('models.User.query')
def test_google_login(mock_user_query, mock_verify_token, client):
    mock_verify_token.return_value = {
        'email': 'google@example.com',
        'sub': '12345',
        'name': 'Google User'
    }
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.email = 'google@example.com'
    mock_user.name = 'Google User'
    mock_user.is_admin = False
    mock_user_query.filter_by.return_value.first.return_value = mock_user
    
    response = client.post('/auth/login/google', json={
        'token': 'fake_google_token'
    })
    assert response.status_code == 200
    assert 'token' in response.json
    assert response.json['user']['email'] == 'google@example.com'
    assert response.json['user']['name'] == 'Google User'

@patch('google.oauth2.id_token.verify_oauth2_token')
def test_google_login_error(mock_verify_token, client):
    mock_verify_token.side_effect = Exception("Test error")
    
    response = client.post('/auth/login/google', json={
        'token': 'fake_google_token'
    })
    assert response.status_code == 500
    assert 'Error in google_login' in response.json['message']

@patch('models.UserJWT.query')
@patch('extensions.db.session')
def test_logout(mock_db_session, mock_user_jwt_query, client):
    # Mock UserJWT query
    mock_user_jwt = MagicMock()
    mock_user_jwt_query.filter_by.return_value.first.return_value = mock_user_jwt

    # Create a test token
    token = 'test_token'

    # Then, logout
    response = client.post('/auth/logout', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json['message'] == 'Logged out successfully'
    mock_user_jwt_query.filter_by.assert_called_once_with(token=token)
    mock_db_session.delete.assert_called_once_with(mock_user_jwt)
    mock_db_session.commit.assert_called_once()

@patch('models.UserJWT.query')
@patch('models.User.query')
@patch('sqlalchemy.func.now')
def test_current_user(mock_func_now, mock_user_query, mock_user_jwt_query, client, app):
    # Mock current time
    current_time = datetime.now(timezone.utc)
    mock_func_now.return_value = current_time

    # Mock User and UserJWT queries
    mock_user = MagicMock()
    mock_user.to_dict.return_value = {
        'email': 'test@example.com',
        'name': 'Test User'
    }
    mock_user_query.get.return_value = mock_user

    mock_user_jwt = MagicMock()
    mock_user_jwt.is_active = True
    mock_user_jwt.expires_at = current_time + timedelta(days=1)
    mock_user_jwt_query.filter_by.return_value.first.return_value = mock_user_jwt

    # Create a test token
    with app.app_context():
        token = PyJWT.encode({'user_id': 1, 'exp': current_time + timedelta(days=1)}, app.config['SECRET_KEY'], algorithm="HS256")

    response = client.get('/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json['email'] == 'test@example.com'
    assert response.json['name'] == 'Test User'

def test_token_required_decorator(client):
    response = client.get('/auth/me')
    assert response.status_code == 401
    assert 'Missing or invalid token format' in response.json['message']

    response = client.get('/auth/me', headers={'Authorization': 'InvalidToken'})
    assert response.status_code == 401
    assert 'Missing or invalid token format' in response.json['message']

    response = client.get('/auth/me', headers={'Authorization': 'Bearer InvalidToken'})
    assert response.status_code == 401
    assert 'Invalid or expired token' in response.json['message']
