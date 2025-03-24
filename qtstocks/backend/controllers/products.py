from flask import request
from flask_restx import Resource, Namespace, fields
from models import Product, db
from datetime import datetime, timezone

def init_product_routes(app, token_required, products_ns):
    """Initialize routes for product management"""
    
    # Model for Swagger documentation
    product_model = products_ns.model('Product', {
        'id': fields.Integer(readonly=True, description='Product ID'),
        'name': fields.String(required=True, description='Product name'),
        'description': fields.String(description='Product description'),
        'price': fields.Float(required=True, description='Product price'),
        'currency': fields.String(description='Currency code (defaults to USD)'),
        'interval': fields.String(required=True, description='Billing interval (monthly, yearly, one-time)'),
        'features': fields.Raw(description='List of features included in this product'),
        'is_active': fields.Boolean(description='Whether the product is active'),
        'created_at': fields.DateTime(readonly=True, description='Creation date'),
        'updated_at': fields.DateTime(readonly=True, description='Last update date')
    })
    
    product_create_model = products_ns.model('ProductCreate', {
        'name': fields.String(required=True, description='Product name'),
        'description': fields.String(description='Product description'),
        'price': fields.Float(required=True, description='Product price'),
        'currency': fields.String(description='Currency code (defaults to USD)'),
        'interval': fields.String(required=True, description='Billing interval (monthly, yearly, one-time)'),
        'features': fields.Raw(description='List of features included in this product')
    })
    
    product_update_model = products_ns.model('ProductUpdate', {
        'name': fields.String(description='Product name'),
        'description': fields.String(description='Product description'),
        'price': fields.Float(description='Product price'),
        'currency': fields.String(description='Currency code'),
        'interval': fields.String(description='Billing interval (monthly, yearly, one-time)'),
        'features': fields.Raw(description='List of features included in this product'),
        'is_active': fields.Boolean(description='Whether the product is active')
    })
    
    @products_ns.route('/')
    class ProductList(Resource):
        @products_ns.doc('list_products')
        @products_ns.marshal_list_with(product_model)
        def get(self):
            """List all products"""
            # Only return active products for non-admin users
            if not hasattr(self, 'current_user') or not self.current_user.is_admin:
                return Product.query.filter_by(is_active=True).all()
            return Product.query.all()
        
        @products_ns.doc('create_product', security='Bearer')
        @products_ns.expect(product_create_model)
        @products_ns.marshal_with(product_model)
        @token_required
        def post(self, current_user):
            """Create a new product (admin only)"""
            if not current_user.is_admin:
                products_ns.abort(403, "Only admin users can create products")
            
            try:
                data = request.get_json()
                
                # Validate interval
                valid_intervals = ['monthly', 'yearly', 'one-time']
                if data['interval'] not in valid_intervals:
                    products_ns.abort(400, f"Invalid interval. Must be one of: {', '.join(valid_intervals)}")
                
                product = Product(
                    name=data['name'],
                    description=data.get('description'),
                    price=data['price'],
                    currency=data.get('currency', 'USD'),
                    interval=data['interval'],
                    features=data.get('features', [])
                )
                
                db.session.add(product)
                db.session.commit()
                return product
            except Exception as e:
                db.session.rollback()
                products_ns.abort(500, message=str(e))
    
    @products_ns.route('/<int:product_id>')
    @products_ns.param('product_id', 'The product identifier')
    class ProductResource(Resource):
        @products_ns.doc('get_product')
        @products_ns.marshal_with(product_model)
        def get(self, product_id):
            """Get a product by ID"""
            product = Product.query.get_or_404(product_id)
            # Only allow access to active products for non-admin users
            if not hasattr(self, 'current_user') or not self.current_user.is_admin:
                if not product.is_active:
                    products_ns.abort(404, "Product not found")
            return product
        
        @products_ns.doc('update_product', security='Bearer')
        @products_ns.expect(product_update_model)
        @products_ns.marshal_with(product_model)
        @token_required
        def put(self, current_user, product_id):
            """Update a product (admin only)"""
            if not current_user.is_admin:
                products_ns.abort(403, "Only admin users can update products")
            
            product = Product.query.get_or_404(product_id)
            
            try:
                data = request.get_json()
                
                # Validate interval if provided
                if 'interval' in data:
                    valid_intervals = ['monthly', 'yearly', 'one-time']
                    if data['interval'] not in valid_intervals:
                        products_ns.abort(400, f"Invalid interval. Must be one of: {', '.join(valid_intervals)}")
                
                if 'name' in data:
                    product.name = data['name']
                if 'description' in data:
                    product.description = data['description']
                if 'price' in data:
                    product.price = data['price']
                if 'currency' in data:
                    product.currency = data['currency']
                if 'interval' in data:
                    product.interval = data['interval']
                if 'features' in data:
                    product.features = data['features']
                if 'is_active' in data:
                    product.is_active = data['is_active']
                
                db.session.commit()
                return product
            except Exception as e:
                db.session.rollback()
                products_ns.abort(500, message=str(e))
        
        @products_ns.doc('delete_product', security='Bearer')
        @token_required
        def delete(self, current_user, product_id):
            """Delete a product (admin only)"""
            if not current_user.is_admin:
                products_ns.abort(403, "Only admin users can delete products")
            
            product = Product.query.get_or_404(product_id)
            
            try:
                # Check if product has any active subscriptions
                active_subs = [sub for sub in product.subscriptions if sub.is_active]
                if active_subs:
                    products_ns.abort(400, "Cannot delete product with active subscriptions")
                
                db.session.delete(product)
                db.session.commit()
                return {'message': 'Product deleted successfully'}
            except Exception as e:
                db.session.rollback()
                products_ns.abort(500, message=str(e))
    
    return products_ns 