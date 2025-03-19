from flask import jsonify, request, Response
from datetime import datetime, timedelta, UTC
import jwt as PyJWT
import os
import requests
from models import User
from extensions import db

def init_auth_routes(app):
    @app.route('/api/login', methods=['POST', 'OPTIONS'])
    def login():
        if request.method == 'OPTIONS':
            return Response()
            
        try:
            # Add debug logging
            print("Received login request")
            print("Request headers:", dict(request.headers))
            print("Request data:", request.get_data())
            
            data = request.get_json()
            if not data:
                print("No JSON data received")
                return jsonify({'success': False, 'message': 'No data received'}), 400
                
            username = data.get('username')
            password = data.get('password')
            
            print(f"Login attempt for username: {username}")
            
            if not username or not password:
                print("Missing username or password")
                return jsonify({'success': False, 'message': 'Please enter both username and password.'}), 400
            
            user = User.query.filter_by(username=username).first()
            if not user:
                print(f"User not found: {username}")
                return jsonify({'success': False, 'message': 'Invalid username or password.'}), 401
                
            if not user.check_password(password):
                print(f"Invalid password for user: {username}")
                return jsonify({'success': False, 'message': 'Invalid username or password.'}), 401
                
            token = PyJWT.encode({
                'user_id': user.id,
                'exp': datetime.now(UTC) + timedelta(days=1)
            }, app.config['SECRET_KEY'], algorithm="HS256")
            
            print(f"Login successful for user: {username}")
            return jsonify({
                'success': True, 
                'message': 'Logged in successfully.',
                'token': token
            })
            
        except Exception as e:
            print(f"Login error: {str(e)}")
            return jsonify({'success': False, 'message': 'An error occurred during login.'}), 500
    
    @app.route('/api/logout', methods=['POST'])
    def logout(current_user):
        return jsonify({'success': True, 'message': 'Logged out successfully.'})
    
    @app.route('/api/login/google', methods=['POST'])
    def google_login():
        try:
            # Get token info from frontend
            data = request.get_json()
            if not data or 'token' not in data:
                return jsonify({'success': False, 'message': 'No token provided'}), 400

            token = data['token']

            # Verify the ID token with Google's OAuth2 API
            google_response = requests.get(
                f'https://oauth2.googleapis.com/tokeninfo?id_token={token}'
            )

            if not google_response.ok:
                return jsonify({'success': False, 'message': 'Failed to verify Google token'}), 401

            google_data = google_response.json()

            # Verify that the token was intended for our app
            if google_data['aud'] != app.config['GOOGLE_CLIENT_ID']:
                return jsonify({'success': False, 'message': 'Invalid token audience'}), 401

            # Get user info from verified token data
            google_id = google_data['sub']
            email = google_data.get('email')
            
            if not email:
                return jsonify({'success': False, 'message': 'Email not provided'}), 400
                
            username = email.split('@')[0]  # Use email prefix as username

            # Find existing user or create new one
            user = User.query.filter_by(google_id=google_id).first()
            if not user:
                # Create new user
                user = User(
                    username=username,
                    email=email,
                    google_id=google_id
                )
                user.set_password(os.urandom(24).hex())  # Set a random password
                db.session.add(user)
                db.session.commit()

            # Create JWT token
            token = PyJWT.encode({
                'user_id': user.id,
                'exp': datetime.now(UTC) + timedelta(days=1)
            }, app.config['SECRET_KEY'], algorithm="HS256")

            return jsonify({
                'success': True,
                'message': 'Logged in with Google successfully',
                'token': token
            })

        except Exception as e:
            print(f"Google login error: {str(e)}")
            return jsonify({'success': False, 'message': 'An error occurred during Google login'}), 500 