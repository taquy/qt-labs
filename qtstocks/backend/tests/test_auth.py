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

@patch('extensions.db.session')
def test_logout(mock_db_session, mock_user_jwt_query, client):
    # Mock the UserJWT query
    mock_user_jwt = MagicMock(spec=UserJWT)
    mock_user_jwt.id = 1
    mock_user_jwt.user_id = 1
    mock_user_jwt.token = "test_token"
    mock_user_jwt.is_active = True
    mock_user_jwt.expires_at = datetime.now(timezone.utc) + timedelta(days=1)
    mock_user_jwt.created_at = datetime.now(timezone.utc)

    # Set up the mock query
    mock_query = MagicMock()
    mock_query.filter_by.return_value.first.return_value = mock_user_jwt
    mock_user_jwt_query.return_value = mock_query

    # Make the API call
    response = client.post('/auth/logout', headers={'Authorization': 'Bearer test_token'})

    # Assert the response
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == "Successfully logged out"

    # Verify that the UserJWT was deleted and committed
    mock_db_session.delete.assert_called_once_with(mock_user_jwt)
    mock_db_session.commit.assert_called_once()

    # Verify that the query was called with the correct token
    mock_query.filter_by.assert_called_once_with(token="test_token")

@patch('models.UserJWT.query')
@patch('models.User.query')
def test_current_user(mock_user_query, mock_user_jwt_query, client):
    # Mock current time
    mock_now = datetime(2025, 3, 28, 12, 0, 0, tzinfo=timezone.utc)
    with patch('controllers.auth.datetime') as mock_datetime:
        mock_datetime.now.return_value = mock_now

        # Mock the User query
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.name = "Test User"
        mock_user.is_admin = False
        mock_user.is_active = True
        mock_user.created_at = mock_now
        mock_user.last_login = mock_now

        # Mock the UserJWT query
        mock_user_jwt = MagicMock(spec=UserJWT)
        mock_user_jwt.id = 1
        mock_user_jwt.user_id = mock_user.id
        mock_user_jwt.token = "test_token"
        mock_user_jwt.is_active = True
        mock_user_jwt.expires_at = mock_now + timedelta(days=1)
        mock_user_jwt.created_at = mock_now

        # Set up the mock queries
        mock_user_query.get.return_value = mock_user
        mock_user_jwt_query.filter_by.return_value.first.return_value = mock_user_jwt

        # Make the API call
        response = client.get('/auth/current_user', headers={'Authorization': 'Bearer test_token'})

        # Assert the response
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == 1
        assert data['email'] == "test@example.com"
        assert data['name'] == "Test User"
        assert data['is_admin'] == False
        assert data['is_active'] == True

        # Verify that the queries were called correctly
        mock_user_query.get.assert_called_once_with(1)
        mock_user_jwt_query.filter_by.assert_called_once_with(token="test_token")

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
