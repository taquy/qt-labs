from flask import jsonify, request
from models import Subscription, Payment, db
from datetime import datetime, timezone, timedelta
from flask_restx import Resource, fields

def init_subscription_routes(app, token_required, subscriptions_ns):
    # Define models for Swagger documentation
    subscription_model = subscriptions_ns.model('Subscription', {
        'id': fields.Integer(readonly=True, description='Subscription ID'),
        'user_id': fields.Integer(required=True, description='User ID'),
        'plan_type': fields.String(required=True, description='Subscription plan type'),
        'status': fields.String(required=True, description='Subscription status'),
        'start_date': fields.DateTime(required=True, description='Start date'),
        'end_date': fields.DateTime(description='End date'),
        'auto_renew': fields.Boolean(description='Auto-renewal status'),
        'payment_id': fields.Integer(description='Associated payment ID'),
        'subscription_metadata': fields.Raw(description='Additional subscription data'),
        'created_at': fields.DateTime(readonly=True, description='Creation date'),
        'updated_at': fields.DateTime(readonly=True, description='Last update date')
    })

    subscription_create_model = subscriptions_ns.model('SubscriptionCreate', {
        'plan_type': fields.String(required=True, description='Subscription plan type'),
        'payment_id': fields.Integer(description='Associated payment ID'),
        'start_date': fields.DateTime(description='Start date (defaults to current date)'),
        'end_date': fields.DateTime(description='End date'),
        'auto_renew': fields.Boolean(description='Auto-renewal status', default=True),
        'subscription_metadata': fields.Raw(description='Additional subscription data')
    })

    subscription_update_model = subscriptions_ns.model('SubscriptionUpdate', {
        'plan_type': fields.String(description='Subscription plan type'),
        'status': fields.String(description='Subscription status'),
        'end_date': fields.DateTime(description='End date'),
        'auto_renew': fields.Boolean(description='Auto-renewal status'),
        'subscription_metadata': fields.Raw(description='Additional subscription data')
    })

    @subscriptions_ns.route('')
    class SubscriptionList(Resource):
        @subscriptions_ns.doc('list_subscriptions', security='Bearer')
        @subscriptions_ns.param('page', 'Page number (1-based)', type=int, default=1)
        @subscriptions_ns.param('per_page', 'Items per page', type=int, default=10)
        @subscriptions_ns.param('status', 'Filter by subscription status', type=str)
        @subscriptions_ns.param('plan_type', 'Filter by plan type', type=str)
        @subscriptions_ns.param('active_only', 'Show only active subscriptions', type=bool)
        @subscriptions_ns.marshal_list_with(subscription_model)
        @token_required
        def get(self, current_user):
            """List all subscriptions for the current user with pagination and filters"""
            try:
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 10, type=int)
                status = request.args.get('status')
                plan_type = request.args.get('plan_type')
                active_only = request.args.get('active_only', type=bool)
                
                # Build query
                query = Subscription.query.filter_by(user_id=current_user.id)
                
                # Apply filters
                if status:
                    query = query.filter(Subscription.status == status)
                if plan_type:
                    query = query.filter(Subscription.plan_type == plan_type)
                if active_only:
                    now = datetime.now(timezone.utc)
                    query = query.filter(
                        Subscription.status == 'active',
                        Subscription.start_date <= now,
                        (Subscription.end_date.is_(None) | (Subscription.end_date > now))
                    )
                
                # Order by creation date (newest first)
                query = query.order_by(Subscription.created_at.desc())
                
                # Paginate
                pagination = query.paginate(page=page, per_page=per_page, error_out=False)
                
                return {
                    'items': pagination.items,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'current_page': page,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            except Exception as e:
                subscriptions_ns.abort(500, message=str(e))

        @subscriptions_ns.doc('create_subscription', security='Bearer')
        @subscriptions_ns.expect(subscription_create_model)
        @subscriptions_ns.marshal_with(subscription_model)
        @token_required
        def post(self, current_user):
            """Create a new subscription"""
            try:
                data = request.get_json()
                
                # Check if user has enough budget for the plan
                plan_price = Subscription.PLAN_PRICES.get(data['plan_type'], 0.0)
                if plan_price > 0 and current_user.budget < plan_price:
                    subscriptions_ns.abort(400, "Insufficient budget for this plan")
                
                # Validate payment if provided
                if data.get('payment_id'):
                    payment = Payment.query.get_or_404(data['payment_id'])
                    if payment.user_id != current_user.id:
                        subscriptions_ns.abort(403, "Invalid payment ID")
                    if payment.status != 'completed':
                        subscriptions_ns.abort(400, "Payment must be completed")
                
                # Create subscription
                subscription = Subscription(
                    user_id=current_user.id,
                    plan_type=data['plan_type'],
                    payment_id=data.get('payment_id'),
                    start_date=data.get('start_date', datetime.now(timezone.utc)),
                    end_date=data.get('end_date'),
                    auto_renew=data.get('auto_renew', True),
                    subscription_metadata=data.get('subscription_metadata'),
                    status='active'
                )
                
                # Deduct plan price from user's budget
                if plan_price > 0:
                    current_user.budget -= plan_price
                
                db.session.add(subscription)
                db.session.commit()
                return subscription
            except Exception as e:
                db.session.rollback()
                subscriptions_ns.abort(500, message=str(e))

    @subscriptions_ns.route('/<int:subscription_id>')
    @subscriptions_ns.param('subscription_id', 'The subscription identifier')
    class SubscriptionResource(Resource):
        @subscriptions_ns.doc('get_subscription', security='Bearer')
        @subscriptions_ns.marshal_with(subscription_model)
        @token_required
        def get(self, current_user, subscription_id):
            """Get a subscription by ID"""
            subscription = Subscription.query.get_or_404(subscription_id)
            if subscription.user_id != current_user.id:
                subscriptions_ns.abort(403, "Access denied")
            return subscription

        @subscriptions_ns.doc('update_subscription', security='Bearer')
        @subscriptions_ns.expect(subscription_update_model)
        @subscriptions_ns.marshal_with(subscription_model)
        @token_required
        def put(self, current_user, subscription_id):
            """Update a subscription"""
            subscription = Subscription.query.get_or_404(subscription_id)
            if subscription.user_id != current_user.id:
                subscriptions_ns.abort(403, "Access denied")
                
            try:
                data = request.get_json()
                
                if 'plan_type' in data:
                    subscription.update_plan(data['plan_type'])
                if 'status' in data:
                    subscription.status = data['status']
                if 'end_date' in data:
                    subscription.end_date = data['end_date']
                if 'auto_renew' in data:
                    subscription.auto_renew = data['auto_renew']
                if 'subscription_metadata' in data:
                    subscription.subscription_metadata = data['subscription_metadata']
                
                db.session.commit()
                return subscription
            except ValueError as e:
                db.session.rollback()
                subscriptions_ns.abort(400, message=str(e))
            except Exception as e:
                db.session.rollback()
                subscriptions_ns.abort(500, message=str(e))

        @subscriptions_ns.doc('delete_subscription', security='Bearer')
        @token_required
        def delete(self, current_user, subscription_id):
            """Delete a subscription"""
            subscription = Subscription.query.get_or_404(subscription_id)
            if subscription.user_id != current_user.id:
                subscriptions_ns.abort(403, "Access denied")
                
            try:
                db.session.delete(subscription)
                db.session.commit()
                return '', 204
            except Exception as e:
                db.session.rollback()
                subscriptions_ns.abort(500, message=str(e))

    @subscriptions_ns.route('/<int:subscription_id>/cancel')
    @subscriptions_ns.param('subscription_id', 'The subscription identifier')
    class SubscriptionCancel(Resource):
        @subscriptions_ns.doc('cancel_subscription', security='Bearer')
        @subscriptions_ns.marshal_with(subscription_model)
        @token_required
        def post(self, current_user, subscription_id):
            """Cancel a subscription"""
            subscription = Subscription.query.get_or_404(subscription_id)
            if subscription.user_id != current_user.id:
                subscriptions_ns.abort(403, "Access denied")
                
            try:
                subscription.cancel()
                db.session.commit()
                return subscription
            except Exception as e:
                db.session.rollback()
                subscriptions_ns.abort(500, message=str(e))

    @subscriptions_ns.route('/<int:subscription_id>/suspend')
    @subscriptions_ns.param('subscription_id', 'The subscription identifier')
    class SubscriptionSuspend(Resource):
        @subscriptions_ns.doc('suspend_subscription', security='Bearer')
        @subscriptions_ns.marshal_with(subscription_model)
        @token_required
        def post(self, current_user, subscription_id):
            """Suspend a subscription"""
            subscription = Subscription.query.get_or_404(subscription_id)
            if subscription.user_id != current_user.id:
                subscriptions_ns.abort(403, "Access denied")
                
            try:
                subscription.suspend()
                db.session.commit()
                return subscription
            except Exception as e:
                db.session.rollback()
                subscriptions_ns.abort(500, message=str(e))

    @subscriptions_ns.route('/<int:subscription_id>/reactivate')
    @subscriptions_ns.param('subscription_id', 'The subscription identifier')
    class SubscriptionReactivate(Resource):
        @subscriptions_ns.doc('reactivate_subscription', security='Bearer')
        @subscriptions_ns.marshal_with(subscription_model)
        @token_required
        def post(self, current_user, subscription_id):
            """Reactivate a suspended subscription"""
            subscription = Subscription.query.get_or_404(subscription_id)
            if subscription.user_id != current_user.id:
                subscriptions_ns.abort(403, "Access denied")
                
            try:
                subscription.reactivate()
                db.session.commit()
                return subscription
            except Exception as e:
                db.session.rollback()
                subscriptions_ns.abort(500, message=str(e))

    @subscriptions_ns.route('/<int:subscription_id>/extend')
    @subscriptions_ns.param('subscription_id', 'The subscription identifier')
    class SubscriptionExtend(Resource):
        @subscriptions_ns.doc('extend_subscription', security='Bearer')
        @subscriptions_ns.expect(subscriptions_ns.model('ExtendSubscription', {
            'days': fields.Integer(required=True, description='Number of days to extend')
        }))
        @subscriptions_ns.marshal_with(subscription_model)
        @token_required
        def post(self, current_user, subscription_id):
            """Extend a subscription by specified number of days"""
            subscription = Subscription.query.get_or_404(subscription_id)
            if subscription.user_id != current_user.id:
                subscriptions_ns.abort(403, "Access denied")
                
            try:
                data = request.get_json()
                days = data.get('days')
                if not days or days <= 0:
                    subscriptions_ns.abort(400, "Invalid number of days")
                    
                subscription.extend(days)
                db.session.commit()
                return subscription
            except Exception as e:
                db.session.rollback()
                subscriptions_ns.abort(500, message=str(e)) 