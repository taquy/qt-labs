from flask import jsonify, request
from models import StockPortfolio, Stock, db
from extensions import ma
from datetime import datetime, timezone
from functools import wraps
from flask_restx import Resource, fields

def init_portfolio_routes(app, token_required, portfolios_ns):
    # Define models for Swagger documentation
    stock_model = portfolios_ns.model('Stock', {
        'symbol': fields.String(required=True, description='Stock symbol'),
        'name': fields.String(required=True, description='Stock name'),
        'icon': fields.String(description='Stock icon URL'),
        'exchange': fields.String(description='Stock exchange'),
        'market_cap': fields.Float(description='Market capitalization')
    })

    portfolio_model = portfolios_ns.model('Portfolio', {
        'id': fields.Integer(readonly=True, description='Portfolio ID'),
        'user_id': fields.Integer(required=True, description='User ID'),
        'name': fields.String(required=True, description='Portfolio name'),
        'description': fields.String(description='Portfolio description'),
        'stocks': fields.List(fields.Nested(stock_model), description='List of stocks in the portfolio'),
        'created_at': fields.DateTime(readonly=True, description='Creation date'),
        'updated_at': fields.DateTime(readonly=True, description='Last update date')
    })

    portfolio_create_model = portfolios_ns.model('PortfolioCreate', {
        'name': fields.String(required=True, description='Portfolio name'),
        'description': fields.String(description='Portfolio description'),
        'stock_symbols': fields.List(fields.String, description='List of stock symbols')
    })

    portfolio_update_model = portfolios_ns.model('PortfolioUpdate', {
        'name': fields.String(description='Portfolio name'),
        'description': fields.String(description='Portfolio description'),
        'stock_symbols': fields.List(fields.String, description='List of stock symbols')
    })

    @portfolios_ns.route('')
    class PortfolioList(Resource):
        @portfolios_ns.doc('list_portfolios', security='Bearer')
        @portfolios_ns.marshal_list_with(portfolio_model)
        @token_required
        def get(self, current_user):
            """List all portfolios for the current user"""
            return StockPortfolio.query.filter_by(user_id=current_user.id).all()

        @portfolios_ns.doc('create_portfolio', security='Bearer')
        @portfolios_ns.expect(portfolio_create_model)
        @portfolios_ns.marshal_with(portfolio_model)
        @token_required
        def post(self, current_user):
            """Create a new portfolio"""
            data = request.get_json()
            
            # Check if portfolio name already exists for this user
            if StockPortfolio.query.filter_by(user_id=current_user.id, name=data['name']).first():
                portfolios_ns.abort(400, "Portfolio name already exists")
            
            # Create portfolio
            portfolio = StockPortfolio(
                user_id=current_user.id,
                name=data['name'],
                description=data.get('description')
            )
            
            # Add stocks if provided
            if 'stock_symbols' in data:
                stocks = Stock.query.filter(Stock.symbol.in_(data['stock_symbols'])).all()
                portfolio.stocks = stocks
            
            db.session.add(portfolio)
            db.session.commit()
            return portfolio

    @portfolios_ns.route('/<int:portfolio_id>')
    @portfolios_ns.param('portfolio_id', 'The portfolio identifier')
    class PortfolioResource(Resource):
        @portfolios_ns.doc('get_portfolio', security='Bearer')
        @portfolios_ns.marshal_with(portfolio_model)
        @token_required
        def get(self, current_user, portfolio_id):
            """Get a portfolio by ID"""
            portfolio = StockPortfolio.query.get_or_404(portfolio_id)
            if portfolio.user_id != current_user.id:
                portfolios_ns.abort(403, "Access denied")
            return portfolio

        @portfolios_ns.doc('update_portfolio', security='Bearer')
        @portfolios_ns.expect(portfolio_update_model)
        @portfolios_ns.marshal_with(portfolio_model)
        @token_required
        def put(self, current_user, portfolio_id):
            """Update a portfolio"""
            portfolio = StockPortfolio.query.get_or_404(portfolio_id)
            if portfolio.user_id != current_user.id:
                portfolios_ns.abort(403, "Access denied")
                
            data = request.get_json()
            
            # Check if new name already exists for this user
            if 'name' in data and data['name'] != portfolio.name:
                if StockPortfolio.query.filter_by(user_id=current_user.id, name=data['name']).first():
                    portfolios_ns.abort(400, "Portfolio name already exists")
                portfolio.name = data['name']
            
            if 'description' in data:
                portfolio.description = data['description']
            
            if 'stock_symbols' in data:
                stocks = Stock.query.filter(Stock.symbol.in_(data['stock_symbols'])).all()
                portfolio.stocks = stocks
            
            db.session.commit()
            return portfolio

        @portfolios_ns.doc('delete_portfolio', security='Bearer')
        @token_required
        def delete(self, current_user, portfolio_id):
            """Delete a portfolio"""
            portfolio = StockPortfolio.query.get_or_404(portfolio_id)
            if portfolio.user_id != current_user.id:
                portfolios_ns.abort(403, "Access denied")
                
            db.session.delete(portfolio)
            db.session.commit()
            return '', 204 