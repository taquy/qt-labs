from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone, timedelta
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
    budget = db.Column(db.Float, default=0.0)  # User's current budget
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Many-to-many relationship with StockStats
    stock_stats = db.relationship('StockStats', secondary='user_stock_stats', backref=db.backref('users', lazy='dynamic'))
    user_settings = db.relationship('UserSettings', backref='owner', lazy=True, uselist=False)
    jwt_tokens = db.relationship('UserJWT', backref='user', lazy=True)
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))

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

    def toggle_admin_status(self, admin_user):
        """Toggle admin status with authorization check"""
        if not admin_user.is_admin:
            raise ValueError("Only admin users can modify admin status")
        if self.id == admin_user.id:
            raise ValueError("Cannot modify your own admin status")
        self.is_admin = not self.is_admin

    def toggle_active_status(self, admin_user):
        """Toggle active status with authorization check"""
        if not admin_user.is_admin:
            raise ValueError("Only admin users can modify active status")
        if self.id == admin_user.id:
            raise ValueError("Cannot modify your own active status")
        self.is_active = not self.is_active

    def has_permission(self, resource, action):
        """Check if user has a specific permission through their roles"""
        for role in self.roles:
            for permission in role.permissions:
                if permission.resource == resource and permission.action == action:
                    return True
        return False
    
    def has_role(self, role_name):
        """Check if user has a specific role"""
        return any(role.name == role_name for role in self.roles)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'is_google_user': self.is_google_user,
            'budget': self.budget,
            'roles': [role.to_dict() for role in self.roles],
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

# Association table for StockPortfolio-Stock many-to-many relationship
portfolio_stocks = db.Table('portfolio_stocks',
    db.Column('portfolio_id', db.Integer, db.ForeignKey('stock_portfolio.id'), primary_key=True),
    db.Column('stock_symbol', db.String(10), db.ForeignKey('stock.symbol'), primary_key=True),
    db.Column('created_at', db.DateTime, default=lambda: datetime.now(timezone.utc))
)

class StockPortfolio(db.Model):
    __tablename__ = 'stock_portfolio'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('portfolios', lazy=True))
    stocks = db.relationship('Stock', secondary=portfolio_stocks, backref=db.backref('portfolios', lazy='dynamic'))
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'name', name='unique_portfolio_name_per_user'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'stocks': [stock.to_dict() for stock in self.stocks],
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
        
    def __repr__(self):
        return f'<StockPortfolio {self.name}>'

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

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='USD')
    payment_method = db.Column(db.String(50), nullable=False)  # e.g., 'credit_card', 'paypal', 'bank_transfer'
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, completed, failed, refunded
    transaction_id = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(255))
    payment_metadata = db.Column(db.JSON)  # For storing additional payment-related data
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = db.relationship('User', backref=db.backref('payments', lazy=True))
    
    def __repr__(self):
        return f'<Payment {self.id} - {self.amount} {self.currency}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'currency': self.currency,
            'payment_method': self.payment_method,
            'status': self.status,
            'transaction_id': self.transaction_id,
            'description': self.description,
            'payment_metadata': self.payment_metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def update_status(self, new_status):
        """Update payment status and handle budget changes"""
        old_status = self.status
        self.status = new_status
        
        if new_status == 'completed' and old_status != 'completed':
            # Add amount to user's budget when payment is completed
            self.user.budget += self.amount
        elif old_status == 'completed' and new_status != 'completed':
            # Remove amount from user's budget if payment is no longer completed
            self.user.budget -= self.amount
        elif new_status == 'refunded' and old_status == 'completed':
            # Remove amount from user's budget when payment is refunded
            self.user.budget -= self.amount

class Product(db.Model):
    """Product model for subscription plans"""
    __tablename__ = 'product'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    interval = db.Column(db.String(20), nullable=False)  # monthly, yearly, one-time
    features = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    subscriptions = db.relationship('Subscription', backref='product', lazy=True)
    roles = db.relationship('Role', secondary='product_roles', backref=db.backref('products', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'currency': self.currency,
            'interval': self.interval,
            'features': self.features,
            'is_active': self.is_active,
            'roles': [role.to_dict() for role in self.roles],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Add association table for Product-Role many-to-many relationship
product_roles = db.Table('product_roles',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=lambda: datetime.now(timezone.utc))
)

class Subscription(db.Model):
    """Subscription model for user subscriptions"""
    __tablename__ = 'subscription'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, suspended, cancelled, expired
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    auto_renew = db.Column(db.Boolean, default=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'))
    subscription_metadata = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = db.relationship('User', backref=db.backref('subscriptions', lazy=True))
    payment = db.relationship('Payment', backref=db.backref('subscriptions', lazy=True))
    
    def __repr__(self):
        return f'<Subscription {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'product': self.product.to_dict() if self.product else None,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'auto_renew': self.auto_renew,
            'payment_id': self.payment_id,
            'metadata': self.subscription_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'roles': [role.to_dict() for role in self.get_user_roles()]
        }
    
    @property
    def is_active(self):
        """Check if subscription is currently active"""
        now = datetime.now(timezone.utc)
        return (
            self.status == 'active' and
            self.start_date <= now and
            (self.end_date is None or self.end_date > now)
        )
    
    def cancel(self):
        """Cancel the subscription"""
        self.status = 'cancelled'
        self.auto_renew = False
        if self.end_date is None:
            # Set end date to current date if not set
            self.end_date = datetime.now(timezone.utc)
    
    def suspend(self):
        """Suspend the subscription"""
        self.status = 'suspended'
    
    def reactivate(self):
        """Reactivate a suspended subscription"""
        if self.status == 'suspended':
            self.status = 'active'
    
    def extend(self, days):
        """Extend the subscription by specified number of days"""
        if self.end_date is None:
            self.end_date = datetime.now(timezone.utc)
        self.end_date += timedelta(days=days)
        self.status = 'active'
        self.auto_renew = True

    def update_plan(self, new_plan_type):
        """Update subscription plan and handle budget changes"""
        if new_plan_type not in self.PLAN_PRICES:
            raise ValueError(f"Invalid plan type: {new_plan_type}")
            
        old_price = self.PLAN_PRICES.get(self.product.interval, 0.0)
        new_price = self.PLAN_PRICES[new_plan_type]
        
        # Calculate price difference
        price_diff = new_price - old_price
        
        # Check if user has enough budget for the upgrade
        if price_diff > 0 and self.user.budget < price_diff:
            raise ValueError("Insufficient budget for plan upgrade")
        
        # Update user's budget
        self.user.budget -= price_diff
        
        # Update plan type
        self.product.interval = new_plan_type

    def get_user_roles(self):
        """Get all roles associated with this subscription's product"""
        return self.product.roles.all() if self.product else []

class StockExchanges(db.Model):
    __tablename__ = 'stock_exchanges'
    __table_args__ = {'info': {'is_view': True}}
    
    exchange = db.Column(db.String(50), primary_key=True)

    def to_dict(self):
        return {
            'exchange': self.exchange
        }

# Association table for Role-Permission many-to-many relationship
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=lambda: datetime.now(timezone.utc))
)

# Association table for User-Role many-to-many relationship
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=lambda: datetime.now(timezone.utc))
)

class Role(db.Model):
    """Role model for user roles"""
    __tablename__ = 'role'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Many-to-many relationship with permissions
    permissions = db.relationship('Permission', secondary=role_permissions, backref=db.backref('roles', lazy='dynamic'))
    # Many-to-many relationship with users
    users = db.relationship('User', secondary=user_roles, backref=db.backref('roles', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Role {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'permissions': [permission.to_dict() for permission in self.permissions],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Permission(db.Model):
    """Permission model for role permissions"""
    __tablename__ = 'permission'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    resource = db.Column(db.String(50), nullable=False)  # e.g., 'user', 'product', 'subscription'
    action = db.Column(db.String(20), nullable=False)    # e.g., 'create', 'read', 'update', 'delete'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Permission {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'resource': self.resource,
            'action': self.action,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 