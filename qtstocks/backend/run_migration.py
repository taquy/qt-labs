from app import create_app
from extensions import db

app = create_app()

with app.app_context():
    from flask_migrate import upgrade
    upgrade() 