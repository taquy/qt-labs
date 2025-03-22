from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), unique=True, nullable=False)
    google_id = db.Column(db.String(100), unique=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Many-to-many relationship with StockStats
    stock_stats = db.relationship('StockStats', secondary='user_stock_stats', backref=db.backref('users', lazy='dynamic'))
    user_settings = db.relationship('UserSettings', backref='owner', lazy=True, uselist=False)
    jwt_tokens = db.relationship('UserJWT', backref='user', lazy=True)

    @property
    def is_google_user(self):
        return self.google_id is not None

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    def set_admin_status(self, is_admin, admin_user):
        """Set admin status with authorization check"""
        if not admin_user.is_admin:
            raise ValueError("Only admin users can modify admin status")
        if self.id == admin_user.id:
            raise ValueError("Cannot modify your own admin status")
        self.is_admin = is_admin

    def set_active_status(self, is_active, admin_user):
        """Set active status with authorization check"""
        if not admin_user.is_admin:
            raise ValueError("Only admin users can modify active status")
        if self.id == admin_user.id:
            raise ValueError("Cannot modify your own active status")
        self.is_active = is_active

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'is_google_user': self.is_google_user,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'last_login': self.last_login.strftime('%Y-%m-%d %H:%M:%S') if self.last_login else None
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
    __tablename__ = 'stock'
    symbol = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(255), nullable=True)
    exchange = db.Column(db.String(50), nullable=True)
    market_cap = db.Column(db.Float, nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    stats = db.relationship('StockStats', backref='stock', uselist=False)

    def to_dict(self):
        return {
            'symbol': self.symbol,
            'name': self.name,
            'icon': self.icon,
            'exchange': self.exchange,
            'market_cap': self.market_cap,
            'last_updated': self.last_updated.strftime('%Y-%m-%d %H:%M:%S') if self.last_updated else None
        }

    @staticmethod
    def from_dict(data):
        return Stock(
            symbol=data['symbol'],
            name=data['name'],
            icon=data['icon'],
            exchange=data['exchange'],
            market_cap=data['market_cap'],
            last_updated=datetime.strptime(data['last_updated'], '%Y-%m-%d %H:%M:%S')
        )

class StockStats(db.Model):
    __tablename__ = 'stock_stats'
    symbol = db.Column(db.String(10), db.ForeignKey('stock.symbol'), primary_key=True)
    price = db.Column(db.Float)
    market_cap = db.Column(db.Float)
    eps = db.Column(db.Float)
    pe = db.Column(db.Float)
    pb = db.Column(db.Float)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

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

class StockExchanges(db.Model):
    __tablename__ = 'stock_exchanges'
    __table_args__ = {'info': {'is_view': True}}
    
    exchange = db.Column(db.String(50), primary_key=True)

    def to_dict(self):
        return {
            'exchange': self.exchange
        } 