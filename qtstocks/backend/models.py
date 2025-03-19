from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(128))
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Many-to-many relationship with StockStats
    stock_stats = db.relationship('StockStats', secondary='user_stock_stats', backref=db.backref('users', lazy='dynamic'))
    user_settings = db.relationship('UserSettings', backref='owner', lazy=True, uselist=False)
    jwt_tokens = db.relationship('UserJWT', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'google_id': self.google_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def __repr__(self):
        return f'<User {self.username}>'

# Association table for User-StockStats many-to-many relationship
user_stock_stats = db.Table('user_stock_stats',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('stock_symbol', db.String(10), db.ForeignKey('stock_stats.symbol'), primary_key=True),
    db.Column('created_at', db.DateTime, default=lambda: datetime.now(timezone.utc))
)

class Stock(db.Model):
    symbol = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100))
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'symbol': self.symbol,
            'name': self.name,
            'last_updated': self.last_updated.strftime('%Y-%m-%d %H:%M:%S')
        }

    @staticmethod
    def from_dict(data):
        return Stock(
            symbol=data['symbol'],
            name=data['name'],
            last_updated=datetime.strptime(data['last_updated'], '%Y-%m-%d %H:%M:%S')
        )

class StockStats(db.Model):
    symbol = db.Column(db.String(10), db.ForeignKey('stock.symbol'), primary_key=True)
    price = db.Column(db.Float)
    market_cap = db.Column(db.Float)
    eps = db.Column(db.Float)
    pe = db.Column(db.Float)
    pb = db.Column(db.Float)
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationship with Stock model
    stock = db.relationship('Stock', backref=db.backref('stats', lazy=True, uselist=False))
    
    def to_dict(self):
        return {
            'symbol': self.symbol,
            'price': self.price,
            'market_cap': self.market_cap,
            'eps': self.eps,
            'pe': self.pe,
            'pb': self.pb,
            'last_updated': self.last_updated.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    @staticmethod
    def from_dict(data):
        return StockStats(
            symbol=data['symbol'],
            price=data['price'],
            market_cap=data['market_cap'],
            eps=data['eps'],
            pe=data['pe'],
            pb=data['pb'],
            last_updated=datetime.strptime(data['last_updated'], '%Y-%m-%d %H:%M:%S')
        )

class UserSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    setting_key = db.Column(db.String(50), nullable=False)
    setting_value = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('user_id', 'setting_key', name='unique_user_setting'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'setting_key': self.setting_key,
            'setting_value': self.setting_value,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    @staticmethod
    def from_dict(data):
        return UserSettings(
            user_id=data['user_id'],
            setting_key=data['setting_key'],
            setting_value=data['setting_value']
        )

class UserJWT(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(500), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<UserJWT {self.user_id}>' 