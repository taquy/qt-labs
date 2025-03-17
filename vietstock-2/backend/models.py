from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

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
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), db.ForeignKey('stock.symbol'), nullable=False)
    price = db.Column(db.Float)
    market_cap = db.Column(db.Float)
    eps = db.Column(db.Float)
    pe_ratio = db.Column(db.Float)
    pb_ratio = db.Column(db.Float)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with Stock model
    stock = db.relationship('Stock', backref=db.backref('stats', lazy=True))
    
    def to_dict(self):
        return {
            'symbol': self.symbol,
            'price': self.price,
            'market_cap': self.market_cap,
            'eps': self.eps,
            'pe_ratio': self.pe_ratio,
            'pb_ratio': self.pb_ratio,
            'last_updated': self.last_updated.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    @staticmethod
    def from_dict(data):
        return StockStats(
            symbol=data['symbol'],
            price=data['price'],
            market_cap=data['market_cap'],
            eps=data['eps'],
            pe_ratio=data['pe_ratio'],
            pb_ratio=data['pb_ratio'],
            last_updated=datetime.strptime(data['last_updated'], '%Y-%m-%d %H:%M:%S')
        ) 