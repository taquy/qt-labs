from flask import Flask, current_app, render_template, jsonify, request, Response, send_file, redirect, url_for, flash, session, send_from_directory
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import plotly
import plotly.express as px
import json
import threading
import queue
from datetime import datetime, timedelta, timezone
import io
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from models import User, Stock, StockStats, UserSettings, user_stock_stats
from config import Config
import requests
from bs4 import BeautifulSoup
from services.get_stock_lists import get_stock_list
from extensions import db, login_manager, cors, init_extensions
import os
import jwt as PyJWT
from functools import wraps
from oauthlib.oauth2 import WebApplicationClient
from services.get_stock_data import process_stock_list
import csv
from controllers.auth import init_auth_routes
from controllers.settings import init_settings_routes
from controllers.stocks import init_stock_routes

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
    
    # Initialize routes and get token_required decorator
    token_required = init_auth_routes(app)
    init_settings_routes(app, token_required)
    init_stock_routes(app, token_required)
    
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