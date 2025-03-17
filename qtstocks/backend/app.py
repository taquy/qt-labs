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
from models import User, Stock, StockStats
from config import Config
import requests
from bs4 import BeautifulSoup
from get_stock_lists import get_stock_list
from extensions import db, login_manager, cors, init_extensions
import os
import jwt as PyJWT
from functools import wraps

# Import process_stock_list after app initialization to avoid circular import
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
                     "origins": "*",
                     "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                     "allow_headers": "*",
                     "supports_credentials": True
                 }})
    
    # Queue for SSE messages
    message_queue = queue.Queue()
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
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
                current_user = User.query.get(data['user_id'])
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
    
    @app.route('/api/logout')
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
                        'name': stock.name
                    }
                    for stock in stocks
                ]
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/update_graph', methods=['POST'])
    @token_required
    def update_graph(current_user):
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data received'}), 400
                
            selected_stocks = data.get('stocks', [])
            selected_metric = data.get('metric', 'Price')
            
            if not selected_stocks:
                return jsonify({'error': 'No stocks selected'}), 400
                
            if not selected_metric:
                return jsonify({'error': 'No metric selected'}), 400
            
            df = load_stock_data()
            if df is None:
                return jsonify({'error': 'Error loading stock data'}), 500
            
            filtered_df = df[df['Symbol'].isin(selected_stocks)]
            
            if filtered_df.empty:
                return jsonify({'error': 'No data found for selected stocks'}), 404
            
            filtered_df = filtered_df.sort_values(by=selected_metric, ascending=True)
            
            fig = px.bar(
                filtered_df,
                x='Symbol',
                y=selected_metric,
                title=f'Comparison of {selected_metric} across Selected Stocks',
                labels={'Symbol': 'Stock Symbol', selected_metric: selected_metric},
                template='plotly_white',
                color='Symbol',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig.update_layout(
                showlegend=True,
                plot_bgcolor='white',
                height=500,
                title_x=0.5,
                title_font_size=20,
                bargap=0.2,
                xaxis=dict(
                    title_font=dict(size=14),
                    tickfont=dict(size=12),
                    gridcolor='lightgray'
                ),
                yaxis=dict(
                    title_font=dict(size=14),
                    tickfont=dict(size=12),
                    gridcolor='lightgray'
                )
            )
            
            return jsonify(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))
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
            stocks = Stock.query.all()
            stock_symbols = [stock.symbol for stock in stocks]
            
            if not stock_symbols:
                return jsonify({'error': 'No stocks found in database'}), 404
                
            process_stock_list(stock_symbols, current_app.app_context)
            
            return jsonify({
                'success': True,
                'message': f'Successfully fetched data for {len(stock_symbols)} stocks'
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
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