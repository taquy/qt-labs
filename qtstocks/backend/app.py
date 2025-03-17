from flask import Flask, current_app, render_template, jsonify, request, Response, send_file, redirect, url_for, flash, session
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import plotly
import plotly.express as px
import json
import threading
import queue
from datetime import datetime, timedelta
import io
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from models import User, Stock, StockStats, UserSettings
from config import Config
import requests
from bs4 import BeautifulSoup
from get_stock_lists import get_stock_list
from extensions import db, login_manager, cors, init_extensions
import os
import jwt as PyJWT
from functools import wraps
from oauthlib.oauth2 import WebApplicationClient
from get_stock_data import process_stock_list

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db = init_extensions(app)
    
    # Configure login manager
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Configure CORS to allow all
    cors.init_app(app, resources={r"/*": {
        "origins": "http://localhost:3000",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": "*",
        "supports_credentials": True
    }})
    
    # Queue for SSE messages
    message_queue = queue.Queue()
    
    # OAuth 2 client setup
    client = WebApplicationClient(app.config['GOOGLE_CLIENT_ID'])
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
        
    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            if 'Authorization' in request.headers:
                token = request.headers['Authorization'].split(" ")[1]
            
            if not token:
                return jsonify({'message': 'Token is missing'}), 401
            
            try:
                data = PyJWT.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
                current_user = db.session.get(User, data['user_id'])
                if not current_user:
                    return jsonify({'message': 'User not found'}), 401
            except:
                return jsonify({'message': 'Token is invalid'}), 401
            
            return f(current_user, *args, **kwargs)
        return decorated
    
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
                'exp': datetime.utcnow() + timedelta(days=1)
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
    @token_required
    def logout(current_user):
        return jsonify({'success': True, 'message': 'Logged out successfully.'})
    
    @app.route('/api/stocks')
    @token_required
    def get_stocks(current_user):
        try:
            stocks = Stock.query.all()
            return jsonify({
                'stocks': [
                    {
                        'symbol': stock.symbol,
                        'name': stock.name,
                        'last_updated': stock.last_updated.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    for stock in stocks
                ]
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/stocks_with_stats')
    @token_required
    def get_stocks_with_stats(current_user):
        try:
            # Query stocks that have stats
            stocks_with_stats = db.session.query(Stock).join(StockStats).all()
            return jsonify({
                'stocks': [
                    {
                        'symbol': stock.symbol,
                        'name': stock.name,
                        'last_updated': stock.stats.last_updated.strftime('%Y-%m-%d %H:%M:%S'),
                        'price': stock.stats.price,
                        'market_cap': stock.stats.market_cap,
                        'eps': stock.stats.eps,
                        'pe': stock.stats.pe,
                        'pb': stock.stats.pb
                    }
                    for stock in stocks_with_stats
                ]
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/settings', methods=['GET'])
    @token_required
    def get_settings(current_user):
        try:
            # Get all settings for the current user
            settings = UserSettings.query.filter_by(user_id=current_user.id).all()
            return jsonify({
                'settings': {setting.setting_key: setting.setting_value for setting in settings}
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/settings/<setting_key>', methods=['PUT'])
    @token_required
    def update_setting(current_user, setting_key):
        try:
            data = request.get_json()
            if not data or 'value' not in data:
                return jsonify({'error': 'No data received'}), 400

            # Find existing setting or create new one
            setting = UserSettings.query.filter_by(
                user_id=current_user.id,
                setting_key=setting_key
            ).first()

            if setting:
                setting.setting_value = data['value']
                setting.updated_at = datetime.utcnow()
            else:
                setting = UserSettings(
                    user_id=current_user.id,
                    setting_key=setting_key,
                    setting_value=data['value']
                )
                db.session.add(setting)

            db.session.commit()
            return jsonify(setting.to_dict())
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/settings/<setting_key>', methods=['DELETE'])
    @token_required
    def delete_setting(current_user, setting_key):
        try:
            setting = UserSettings.query.filter_by(
                user_id=current_user.id,
                setting_key=setting_key
            ).first()

            if setting:
                db.session.delete(setting)
                db.session.commit()
                return jsonify({'message': 'Setting deleted successfully'})
            return jsonify({'message': 'Setting not found'}), 404
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/update_graph', methods=['POST'])
    @token_required
    def update_graph(current_user):
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data received'}), 400
            print(data);
            selected_stocks = data.get('stocks', [])
            selected_metric = data.get('metric', 'Price')
            
            if not selected_stocks:
                return jsonify({'error': 'No stocks selected'}), 400
                
            if not selected_metric:
                return jsonify({'error': 'No metric selected'}), 400
            
            # Query stocks with stats from database
            stocks_with_stats = db.session.query(Stock).join(StockStats).filter(Stock.symbol.in_(selected_stocks)).all()
            
            if not stocks_with_stats:
                return jsonify({'error': 'No data found for selected stocks'}), 404
            
            # Create data structure for frontend
            metric_mapping = {
                'Price': 'price',
                'Market Cap': 'market_cap',
                'EPS': 'eps',
                'P/E': 'pe',
                'P/B': 'pb'
            }
            
            # Return data in a format suitable for frontend plotting
            plot_data = [
                {
                    'symbol': stock.symbol,
                    'value': getattr(stock.stats, metric_mapping[selected_metric]),
                    'name': stock.name,
                    'last_updated': stock.stats.last_updated.strftime('%Y-%m-%d %H:%M:%S')
                }
                for stock in stocks_with_stats
            ]
            
            # Sort data by the selected metric
            plot_data.sort(key=lambda x: x['value'])
            
            return jsonify({
                'data': plot_data,
                'metric': selected_metric
            })
            
        except Exception as e:
            print(f"Error in update_graph: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/download_stock_list', methods=['POST'])
    @token_required
    def download_stock_list(current_user):
        try:
            stocks = get_stock_list()
            
            for stock_data in stocks:
                existing_stock = Stock.query.filter_by(symbol=stock_data['Symbol']).first()
                if not existing_stock:
                    stock = Stock(
                        symbol=stock_data['Symbol'],
                        name=stock_data['Name'],
                        last_updated=datetime.utcnow()
                    )
                    db.session.add(stock)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Successfully downloaded {len(stocks)} stocks'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/fetch_stock_data', methods=['POST'])
    @token_required
    def fetch_stock_data(current_user):
        try:
            data = request.get_json()
            if not data or 'symbols' not in data:
                return jsonify({'error': 'No stock symbols provided'}), 400
                
            symbols = data['symbols']
            if not symbols:
                return jsonify({'error': 'Empty stock symbols list'}), 400
            
            # Verify all symbols exist in database
            for symbol in symbols:
                stock = Stock.query.filter_by(symbol=symbol).first()
                if not stock:
                    return jsonify({'error': f'Stock {symbol} not found in database'}), 404
            
            process_stock_list(symbols)
            
            return jsonify({
                'success': True,
                'message': f'Successfully fetched data for {len(symbols)} stocks'
            })
            
        except Exception as e:
            print(f"Error in fetch_stock_data: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
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
                'exp': datetime.utcnow() + timedelta(days=1)
            }, app.config['SECRET_KEY'], algorithm="HS256")

            return jsonify({
                'success': True,
                'message': 'Logged in with Google successfully',
                'token': token
            })

        except Exception as e:
            print(f"Google login error: {str(e)}")
            return jsonify({'success': False, 'message': 'An error occurred during Google login'}), 500
    
    # Serve React app
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')
    
    # Initialize database and create admin user
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(username=Config.ADMIN_USERNAME).first()
        if not admin:
            admin = User(username=Config.ADMIN_USERNAME)
            admin.set_password(Config.ADMIN_PASSWORD)
            db.session.add(admin)
            db.session.commit()
            print(f"Admin user '{Config.ADMIN_USERNAME}' created successfully!")
        else:
            print(f"Admin user '{Config.ADMIN_USERNAME}' already exists.")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5555) 