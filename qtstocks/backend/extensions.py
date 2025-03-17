from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from flask_migrate import Migrate

# Create single instances of extensions
db = SQLAlchemy()
login_manager = LoginManager()
cors = CORS()
migrate = Migrate()

def init_extensions(app):
    """Initialize all extensions with the app"""
    db.init_app(app)
    login_manager.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)
    return db 