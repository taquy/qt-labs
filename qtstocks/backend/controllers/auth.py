from flask import jsonify, request, current_app
from datetime import datetime, timedelta, timezone
from models import User, UserJWT
from extensions import db
import jwt as PyJWT
from google.oauth2 import id_token
from google.auth.transport import requests
from functools import wraps
import secrets

def init_auth_routes(app):
    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            if 'Authorization' in request.headers:
                token = request.headers['Authorization'].split(" ")[1]
            
            if not token:
                return jsonify({'message': 'Token is missing'}), 401
            
            try:
                # First check if token exists in database
                user_jwt = UserJWT.query.filter_by(token=token).first()
                if not user_jwt:
                    return jsonify({'message': 'Token is invalid'}), 401
                
                # Check if token is expired
                current_time = datetime.now(timezone.utc)
                expires_at = user_jwt.expires_at.replace(tzinfo=timezone.utc)
                if expires_at < current_time:
                    # Remove expired token
                    db.session.delete(user_jwt)
                    db.session.commit()
                    return jsonify({'message': 'Token has expired'}), 401
                
                # Decode token to get user
                data = PyJWT.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
                current_user = User.query.get(data['user_id'])
                if not current_user:
                    # Remove token if user not found
                    db.session.delete(user_jwt)
                    db.session.commit()
                    return jsonify({'message': 'User not found'}), 401
                
                return f(current_user, *args, **kwargs)
            except Exception as e:
                print(f"Error in token_required: {str(e)}")
                # Remove invalid token
                if user_jwt:
                    db.session.delete(user_jwt)
                    db.session.commit()
                return jsonify({'message': 'Token is invalid'}), 401
        return decorated
    
    @app.route('/api/login', methods=['POST'])
    def login():
        try:
            data = request.get_json()
            if not data or 'username' not in data or 'password' not in data:
                return jsonify({'error': 'Missing username or password'}), 400
            
            user = User.query.filter_by(username=data['username']).first()
            if not user or not user.check_password(data['password']):
                return jsonify({'error': 'Invalid username or password'}), 401
            
            # Generate JWT token
            current_time = datetime.now(timezone.utc)
            token = PyJWT.encode({
                'user_id': user.id,
                'exp': current_time + timedelta(days=1)
            }, app.config['SECRET_KEY'], algorithm="HS256")
            
            # Store token in database
            user_jwt = UserJWT(
                user_id=user.id,
                token=token,
                expires_at=current_time + timedelta(days=1)
            )
            db.session.add(user_jwt)
            db.session.commit()
            
            return jsonify({
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            })
            
        except Exception as e:
            print(f"Error in login: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/login/google', methods=['POST'])
    def google_login():
        try:
            data = request.get_json()
            if not data or 'token' not in data:
                return jsonify({'error': 'Missing Google token'}), 400
            
            # Verify the token with Google
            idinfo = id_token.verify_oauth2_token(
                data['token'],
                requests.Request(),
                app.config['GOOGLE_CLIENT_ID']
            )
            
            # Get user email from token
            email = idinfo['email']
            
            # Check if user exists
            user = User.query.filter_by(email=email).first()
            if not user:
                # Create new user with a random password
                random_password = secrets.token_urlsafe(32)
                user = User(
                    username=email.split('@')[0],
                    email=email,
                    google_id=idinfo['sub']
                )
                user.set_password(random_password)
                db.session.add(user)
                db.session.commit()
            
            # Generate JWT token
            current_time = datetime.now(timezone.utc)
            token = PyJWT.encode({
                'user_id': user.id,
                'exp': current_time + timedelta(days=1)
            }, app.config['SECRET_KEY'], algorithm="HS256")
            
            # Store token in database
            user_jwt = UserJWT(
                user_id=user.id,
                token=token,
                expires_at=current_time + timedelta(days=1)
            )
            db.session.add(user_jwt)
            db.session.commit()
            
            return jsonify({
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            })
            
        except Exception as e:
            print(f"Error in google_login: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/logout', methods=['POST'])
    @token_required
    def logout(current_user):
        try:
            # Get token from request
            token = request.headers['Authorization'].split(" ")[1]
            
            # Find and remove the token
            user_jwt = UserJWT.query.filter_by(token=token).first()
            if user_jwt:
                db.session.delete(user_jwt)
                db.session.commit()
            
            return jsonify({'message': 'Successfully logged out'})
            
        except Exception as e:
            print(f"Error in logout: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/register', methods=['POST'])
    def register():
        try:
            data = request.get_json()
            if not data or 'username' not in data or 'password' not in data:
                return jsonify({'error': 'Missing username or password'}), 400
            
            if User.query.filter_by(username=data['username']).first():
                return jsonify({'error': 'Username already exists'}), 400
            
            user = User(username=data['username'])
            user.set_password(data['password'])
            if 'email' in data:
                user.email = data['email']
            
            db.session.add(user)
            db.session.commit()
            
            return jsonify({'message': 'User created successfully'})
            
        except Exception as e:
            db.session.rollback()
            print(f"Error in register: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    return token_required 