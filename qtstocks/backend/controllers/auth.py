from flask import jsonify, request, current_app
from datetime import datetime, timedelta, timezone
from models import User, UserJWT
from extensions import db
import jwt as PyJWT
from google.oauth2 import id_token
from google.auth.transport import requests
from functools import wraps
import secrets
from flask_restx import Resource, fields
from google.auth.exceptions import InvalidValue

def init_auth_routes(app, auth_ns):
    # Define models for Swagger documentation
    login_model = auth_ns.model('Login', {
        'email': fields.String(required=True, description='User email'),
        'password': fields.String(required=True, description='User password')
    })

    register_model = auth_ns.model('Register', {
        'email': fields.String(required=True, description='User email'),
        'password': fields.String(required=True, description='User password'),
        'name': fields.String(description='User name')
    })

    google_login_model = auth_ns.model('GoogleLogin', {
        'token': fields.String(required=True, description='Google ID token')
    })

    @auth_ns.route('/login')
    class Login(Resource):
        @auth_ns.doc('login')
        @auth_ns.expect(login_model)
        def post(self):
            """Login with email and password"""
            data = request.get_json()
            if not data or not data.get('email') or not data.get('password'):
                auth_ns.abort(400, "Missing email or password")
            
            user = User.query.filter_by(email=data['email']).first()
            if not user or not user.check_password(data['password']):
                auth_ns.abort(401, "Invalid email or password")
            
            # Update last login
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            
            # Generate JWT token
            token = PyJWT.encode({
                'user_id': user.id,
                'exp': datetime.utcnow() + timedelta(days=1)
            }, current_app.config['SECRET_KEY'], algorithm="HS256")
            
            # Store token in database
            user_jwt = UserJWT(
                user_id=user.id,
                token=token,
                expires_at=datetime.utcnow() + timedelta(days=1)
            )
            db.session.add(user_jwt)
            db.session.commit()
            
            return {
                'token': token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'is_admin': user.is_admin
                }
            }

    @auth_ns.route('/register')
    class Register(Resource):
        @auth_ns.doc('register')
        @auth_ns.expect(register_model)
        def post(self):
            """Register a new user"""
            data = request.get_json()
            if not data or not data.get('email') or not data.get('password'):
                auth_ns.abort(400, "Missing email or password")
            
            if User.query.filter_by(email=data['email']).first():
                auth_ns.abort(400, "Email already registered")
            
            user = User(
                email=data['email'],
                name=data.get('name', '')
            )
            user.set_password(data['password'])
            
            db.session.add(user)
            db.session.commit()
            
            return {
                'message': 'User registered successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name
                }
            }, 201

    @auth_ns.route('/login/google')
    class GoogleLogin(Resource):
        @auth_ns.doc('google_login')
        @auth_ns.expect(google_login_model)
        def post(self):
            """Login with Google"""
            data = request.get_json()
            if not data or not data.get('token'):
                auth_ns.abort(400, "Missing Google token")
            
            try:
                # Verify the token
                idinfo = id_token.verify_oauth2_token(
                    data['token'],
                    requests.Request(),
                    current_app.config['GOOGLE_CLIENT_ID']
                )
                
                # Get user email from token
                email = idinfo['email']
                
                # Find or create user
                user = User.query.filter_by(email=email).first()
                if not user:
                    # Create new user with random password
                    random_password = secrets.token_urlsafe(32)
                    user = User(
                        email=email,
                        name=idinfo.get('name', ''),
                        google_id=idinfo['sub']
                    )
                    user.set_password(random_password)
                    db.session.add(user)
                    db.session.commit()
                
                # Update last login
                user.last_login = datetime.now(timezone.utc)
                db.session.commit()
                
                # Generate JWT token
                token = PyJWT.encode({
                    'user_id': user.id,
                    'exp': datetime.utcnow() + timedelta(days=1)
                }, current_app.config['SECRET_KEY'], algorithm="HS256")
                
                # Store token in database
                user_jwt = UserJWT(
                    user_id=user.id,
                    token=token,
                    expires_at=datetime.utcnow() + timedelta(days=1)
                )
                db.session.add(user_jwt)
                db.session.commit()
                
                return {
                    'token': token,
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'name': user.name,
                        'is_admin': user.is_admin
                    }
                }
                
            except InvalidValue as e:
                auth_ns.abort(401, f"Invalid Google token: {str(e)}")
            except Exception as e:
                auth_ns.abort(500, f"Error in google_login: {str(e)}")

    @auth_ns.route('/logout')
    class Logout(Resource):
        @auth_ns.doc('logout', security='Bearer')
        def post(self):
            """Logout user"""
            token = request.headers.get('Authorization')
            if token and token.startswith('Bearer '):
                token = token.split(' ')[1]
                user_jwt = UserJWT.query.filter_by(token=token).first()
                if user_jwt:
                    db.session.delete(user_jwt)
                    db.session.commit()
            
            return {'message': 'Logged out successfully'}

    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token or not token.startswith('Bearer '):
                auth_ns.abort(401, "Missing or invalid token format")
            
            token = token.split(' ')[1]
            try:
                # Check if token exists and is valid in database
                user_jwt = UserJWT.query.filter_by(token=token).first()
                if not user_jwt or not user_jwt.is_active or user_jwt.expires_at < datetime.utcnow():
                    if user_jwt:
                        db.session.delete(user_jwt)
                        db.session.commit()
                    auth_ns.abort(401, "Invalid or expired token")
                
                # Verify token signature
                data = PyJWT.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
                current_user = User.query.get(data['user_id'])
                if not current_user:
                    db.session.delete(user_jwt)
                    db.session.commit()
                    auth_ns.abort(401, "User not found")
                
                kwargs['current_user'] = current_user
                return f(*args, **kwargs)
                
            except PyJWT.ExpiredSignatureError:
                if user_jwt:
                    db.session.delete(user_jwt)
                    db.session.commit()
                auth_ns.abort(401, "Token has expired")
            except PyJWT.InvalidTokenError:
                if user_jwt:
                    db.session.delete(user_jwt)
                    db.session.commit()
                auth_ns.abort(401, "Invalid token")
        
        return decorated

    return token_required 