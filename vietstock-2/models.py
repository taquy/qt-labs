from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def get_id(self):
        return str(self.id)

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    market_cap = db.Column(db.Float)
    eps = db.Column(db.Float)
    pe_ratio = db.Column(db.Float)
    pb_ratio = db.Column(db.Float)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'symbol': self.symbol,
            'name': self.name,
            'price': self.price,
            'market_cap': self.market_cap,
            'eps': self.eps,
            'pe_ratio': self.pe_ratio,
            'pb_ratio': self.pb_ratio
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            symbol=data.get('Symbol'),
            name=data.get('Name'),
            price=data.get('Price'),
            market_cap=data.get('MarketCap'),
            eps=data.get('EPS'),
            pe_ratio=data.get('P/E'),
            pb_ratio=data.get('P/B')
        ) 