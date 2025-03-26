from datetime import datetime, timezone
import random
from faker import Faker
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import User, db
from app import create_app

fake = Faker()

def generate_mock_users(num_users=100):
    """Generate mock users with various roles and statuses"""
    app = create_app()
    
    with app.app_context():
        # Get existing emails to avoid duplicates
        existing_emails = {user.email for user in User.query.all()}
        
        # Create some admin users
        admin_users = [
            {
                'email': 'admin@example.com',
                'name': 'System Administrator',
                'is_admin': True,
                'is_active': True,
                'google_id': None
            },
            {
                'email': 'superadmin@example.com',
                'name': 'Super Administrator',
                'is_admin': True,
                'is_active': True,
                'google_id': None
            }
        ]
        
        # Create regular users
        regular_users = []
        for _ in range(num_users):
            is_google_user = random.choice([True, False])
            email = fake.email()
            existing_emails.add(email)  # Add to set to prevent future duplicates
            
            user_data = {
                'email': email,
                'name': fake.name(),
                'is_admin': False,
                'is_active': random.choice([True, False]),
                'google_id': fake.uuid4() if is_google_user else None
            }
            regular_users.append(user_data)
        
        # Combine all users
        all_users = admin_users + regular_users
        
        # Create users in database
        for user_data in all_users:
            # Check if user already exists
            existing_user = User.query.filter_by(email=user_data['email']).first()
            if existing_user:
                print(f"User with email {user_data['email']} already exists, skipping...")
                continue
                
            # Create new user
            user = User(
                email=user_data['email'],
                name=user_data['name'],
                is_admin=user_data['is_admin'],
                is_active=user_data['is_active'],
                google_id=user_data['google_id']
            )
            
            # Set password for all users (including Google users)
            # For Google users, we'll set a random password since they won't use it
            password = 'password123' if not user_data['google_id'] else fake.password()
            user.set_password(password)
            
            db.session.add(user)
            print(f"Created user: {user_data['email']}")
        
        db.session.commit()
        print(f"\nSuccessfully created {len(all_users)} users:")
        print(f"- {len(admin_users)} admin users")
        print(f"- {len(regular_users)} regular users")
        print(f"- {len([u for u in regular_users if u['google_id']])} Google users")
        print(f"- {len([u for u in regular_users if u['is_active']])} active users")

if __name__ == '__main__':
    generate_mock_users() 