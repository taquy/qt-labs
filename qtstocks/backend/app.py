from flask import Flask, current_app, render_template, jsonify, request, Response, send_file, redirect, url_for, flash, session, send_from_directory
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restx import Api, Resource, fields, Namespace
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
from extensions import db, login_manager, cors, init_extensions, ma, migrate
import os
import jwt as PyJWT
from functools import wraps
from oauthlib.oauth2 import WebApplicationClient
from services.get_stock_data import process_stock_list
import csv
from controllers.auth import init_auth_routes
from controllers.settings import init_settings_routes
from controllers.stocks import init_stock_routes
from controllers.users import init_user_routes
from controllers.portfolios import init_portfolio_routes
from controllers.payments import init_payment_routes
from controllers.subscriptions import init_subscription_routes

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize Swagger
    api = Api(app, version='1.0', title='QT Stocks API',
              description='API for QT Stocks application',
              doc='/api/docs')
    
    # Create namespaces
    auth_ns = Namespace('auth', description='Authentication operations')
    users_ns = Namespace('users', description='User management operations')
    stocks_ns = Namespace('stocks', description='Stock operations')
    settings_ns = Namespace('settings', description='User settings operations')
    portfolios_ns = Namespace('portfolios', description='Stock portfolio operations')
    payments_ns = Namespace('payments', description='Payment operations')
    subscriptions_ns = Namespace('subscriptions', description='Subscription operations')
    
    # Add namespaces to API
    api.add_namespace(auth_ns)
    api.add_namespace(users_ns)
    api.add_namespace(stocks_ns)
    api.add_namespace(settings_ns)
    api.add_namespace(portfolios_ns)
    api.add_namespace(payments_ns)
    api.add_namespace(subscriptions_ns)
    
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
    token_required = init_auth_routes(app, auth_ns)
    init_settings_routes(app, token_required, settings_ns)
    init_stock_routes(app, token_required, stocks_ns)
    init_user_routes(app, token_required, users_ns)
    init_portfolio_routes(app, token_required, portfolios_ns)
    init_payment_routes(app, token_required, payments_ns)
    init_subscription_routes(app, token_required, subscriptions_ns)
    
    # Initialize database
    with app.app_context():
        # Create admin user if it doesn't exist
        admin = User.query.filter_by(username=Config.ADMIN_USERNAME).first()
        if not admin:
            admin = User(
                username=Config.ADMIN_USERNAME,
                email='admin@example.com',
                name='Admin',
                is_admin=True
            )
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