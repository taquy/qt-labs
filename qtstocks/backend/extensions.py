from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS

# Create single instances of extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
cors = CORS()

def init_extensions(app):
    """Initialize all extensions with the app"""
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    cors.init_app(app)
    return db 