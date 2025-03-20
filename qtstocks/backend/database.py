from extensions import init_extensions
from models import User
from config import Config
from flask_migrate import upgrade

def init_db(app):
    """Initialize database with Flask app"""
    db = init_extensions(app)
    
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(username=Config.ADMIN_USERNAME).first()
        
        if not admin:
            # Create admin user
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
        
        print("Database initialized successfully!")
        return db 