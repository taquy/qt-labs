from flask import Flask, jsonify
from flask_restx import Api, Namespace
import queue
from datetime import datetime, timezone
from models import User
from config import Config
from extensions import db, login_manager, init_extensions   
from controllers.auth import init_auth_routes
from controllers.settings import init_settings_routes
from controllers.stocks import init_stock_routes
from controllers.users import init_user_routes
from controllers.portfolios import init_portfolio_routes
from controllers.payments import init_payment_routes
from controllers.subscriptions import init_subscription_routes
from controllers.products import init_product_routes
from controllers.roles import init_role_routes
from sqlalchemy import text
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure login manager
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Initialize extensions
    init_extensions(app)
    
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
    products_ns = Namespace('products', description='Product management operations')
    roles_ns = Namespace('roles', description='Role and permission operations')
    
    # Add namespaces to API
    api.add_namespace(auth_ns)
    api.add_namespace(users_ns)
    api.add_namespace(stocks_ns)
    api.add_namespace(settings_ns)
    api.add_namespace(portfolios_ns)
    api.add_namespace(payments_ns)
    api.add_namespace(subscriptions_ns)
    api.add_namespace(products_ns)
    api.add_namespace(roles_ns)
    
    @app.route('/health')
    def health_check():
        try:
            # Check database connection
            db.session.execute(text('SELECT 1'))
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 503
    
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
    init_product_routes(app, token_required, products_ns)
    init_role_routes(app, token_required, roles_ns)
    
    # Initialize database (comment out when run flask db upgrade)
    # Temporarily commenting out admin user creation for database migration
    # with app.app_context():
    #     # Create admin user if it doesn't exist
    #     admin = User.query.filter_by(email=Config.ADMIN_EMAIL).first()
    #     if not admin:
    #         admin = User(
    #             email=Config.ADMIN_EMAIL,
    #             name='Admin',
    #             is_admin=True
    #         )
    #         admin.set_password(Config.ADMIN_PASSWORD)
    #         db.session.add(admin)
    #         db.session.commit()
    #         print(f"Admin user '{Config.ADMIN_EMAIL}' created successfully!")
    #     else:
    #         print(f"Admin user '{Config.ADMIN_EMAIL}' already exists.")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5555) 