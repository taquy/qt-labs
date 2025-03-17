from app import app, db
from models import User
from config import Config

def create_admin_user():
    with app.app_context():
        # Check if admin user already exists
        admin = User.query.filter_by(username=Config.ADMIN_USERNAME).first()
        
        if not admin:
            # Create new admin user
            admin = User(username=Config.ADMIN_USERNAME)
            admin.set_password(Config.ADMIN_PASSWORD)
            db.session.add(admin)
            db.session.commit()
            print(f"Admin user '{Config.ADMIN_USERNAME}' created successfully!")
        else:
            print(f"Admin user '{Config.ADMIN_USERNAME}' already exists.")

if __name__ == "__main__":
    create_admin_user() 