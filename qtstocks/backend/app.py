from flask import Flask, current_app, render_template, jsonify, request, Response, send_file, redirect, url_for, flash, session, send_from_directory
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import plotly
import plotly.express as px
import json
import threading
import queue
from datetime import datetime, timedelta, UTC
import io
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from models import User, Stock, StockStats, UserSettings, user_stock_stats
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
import csv
from controllers.auth import init_auth_routes
from controllers.settings import init_settings_routes

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
    
    # Initialize routes
    init_auth_routes(app)
    init_settings_routes(app, token_required)
    
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
            stocks_with_stats = db.session.query(Stock).join(StockStats).join(user_stock_stats).filter(user_stock_stats.c.user_id == current_user.id).all()
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
    
    @app.route('/api/download_stock_list', methods=['POST'])
    @token_required
    def download_stock_list(current_user):
        try:
            stocks = get_stock_list()
            
            for stock_data in stocks:
                existing_stock = Stock.query.filter_by(symbol=stock_data['Symbol']).first()
                if existing_stock:
                    continue
                stock = Stock(
                    symbol=stock_data['Symbol'],
                    name=stock_data['Name'],
                    last_updated=datetime.now(UTC)
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
            
            fetching_latest = data.get('loadLatestData', False)
            
            # Verify all symbols exist in database
            for symbol in symbols:
                stock = Stock.query.filter_by(symbol=symbol).first()
                if not stock:
                    return jsonify({'error': f'Stock {symbol} not found in database'}), 404
                
            if fetching_latest:
                new_symbols = symbols
            else:
                # reuse existing stock stats if already available in stock_stats table
                new_symbols = []
                for symbol in symbols:
                    stock_stat = StockStats.query.filter_by(symbol=symbol).first()
                    if stock_stat:
                        if stock_stat not in current_user.stock_stats:
                            current_user.stock_stats.append(stock_stat)
                    else:
                        new_symbols.append(symbol)
                db.session.commit()
            
            # scrape data for any new symbols
            if len(new_symbols) > 0:
                process_stock_list(new_symbols, current_user)
            
            return jsonify({
                'success': True,
                'message': f'Successfully fetched data for {len(new_symbols)} stocks {", ".join(new_symbols)}'
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
    
    @app.route('/api/remove_stock_stats', methods=['POST'])
    @token_required
    def remove_stock_stats(current_user):
        try:
            data = request.get_json()
            if not data or 'symbols' not in data:
                return jsonify({'error': 'No stock symbols provided'}), 400
                
            symbols = data['symbols']
            if not symbols:
                return jsonify({'error': 'Empty stock symbols list'}), 400
            
            # Delete stats for each symbol
            for symbol in symbols:
                stats = StockStats.query.filter_by(symbol=symbol).first()
                if stats:
                    db.session.delete(stats)
            
            # Delete user_stock_stats for each symbol
            for symbol in symbols:
                user_stock_stat = db.session.query(user_stock_stats).filter_by(stock_symbol=symbol, user_id=current_user.id).first()
                if user_stock_stat:
                    db.session.delete(user_stock_stat)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Successfully removed stats for {len(symbols)} stocks'
            })
            
        except Exception as e:
            db.session.rollback()
            print(f"Error in remove_stock_stats: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/stocks/export')
    @token_required
    def export_stocks(current_user):
        try:
            # Get all stocks with their stats
            stocks = Stock.query.all()
            
            # Create CSV data
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['Symbol', 'Name', 'Price', 'Market Cap', 'EPS', 'P/E', 'P/B', 'Last Updated'])
            
            # Write data
            for stock in stocks:
                stats = StockStats.query.filter_by(symbol=stock.symbol).first()
                writer.writerow([
                    stock.symbol,
                    stock.name,
                    stats.price if stats else '',
                    stats.market_cap if stats else '',
                    stats.eps if stats else '',
                    stats.pe if stats else '',
                    stats.pb if stats else '',
                    stats.last_updated.strftime('%Y-%m-%d %H:%M:%S') if stats else ''
                ])
            
            # Create response
            output.seek(0)
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename=stocks_{datetime.now(UTC).strftime("%Y%m%d_%H%M%S")}.csv'
                }
            )
            
        except Exception as e:
            print(f"Error exporting stocks: {str(e)}")
            return {'error': str(e)}, 500
    
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