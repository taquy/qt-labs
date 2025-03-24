from flask import jsonify, request
from models import Payment, db
from datetime import datetime, timezone
from flask_restx import Resource, fields

def init_payment_routes(app, token_required, payments_ns):
    # Define models for Swagger documentation
    payment_model = payments_ns.model('Payment', {
        'id': fields.Integer(readonly=True, description='Payment ID'),
        'user_id': fields.Integer(required=True, description='User ID'),
        'amount': fields.Float(required=True, description='Payment amount'),
        'currency': fields.String(required=True, description='Currency code'),
        'payment_method': fields.String(required=True, description='Payment method'),
        'status': fields.String(required=True, description='Payment status'),
        'transaction_id': fields.String(description='Transaction ID'),
        'description': fields.String(description='Payment description'),
        'payment_metadata': fields.Raw(description='Additional payment data'),
        'created_at': fields.DateTime(readonly=True, description='Creation date'),
        'updated_at': fields.DateTime(readonly=True, description='Last update date')
    })

    payment_create_model = payments_ns.model('PaymentCreate', {
        'amount': fields.Float(required=True, description='Payment amount'),
        'currency': fields.String(description='Currency code (defaults to USD)'),
        'payment_method': fields.String(required=True, description='Payment method'),
        'transaction_id': fields.String(description='Transaction ID'),
        'description': fields.String(description='Payment description'),
        'payment_metadata': fields.Raw(description='Additional payment data')
    })

    payment_update_model = payments_ns.model('PaymentUpdate', {
        'status': fields.String(description='Payment status'),
        'description': fields.String(description='Payment description'),
        'payment_metadata': fields.Raw(description='Additional payment data')
    })

    @payments_ns.route('')
    class PaymentList(Resource):
        @payments_ns.doc('list_payments', security='Bearer')
        @payments_ns.param('page', 'Page number (1-based)', type=int, default=1)
        @payments_ns.param('per_page', 'Items per page', type=int, default=10)
        @payments_ns.param('status', 'Filter by payment status', type=str)
        @payments_ns.param('payment_method', 'Filter by payment method', type=str)
        @payments_ns.param('start_date', 'Filter by start date (YYYY-MM-DD)', type=str)
        @payments_ns.param('end_date', 'Filter by end date (YYYY-MM-DD)', type=str)
        @payments_ns.marshal_list_with(payment_model)
        @token_required
        def get(self, current_user):
            """List all payments for the current user with pagination and filters"""
            try:
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 10, type=int)
                status = request.args.get('status')
                payment_method = request.args.get('payment_method')
                start_date = request.args.get('start_date')
                end_date = request.args.get('end_date')
                
                # Build query
                query = Payment.query.filter_by(user_id=current_user.id)
                
                # Apply filters
                if status:
                    query = query.filter(Payment.status == status)
                if payment_method:
                    query = query.filter(Payment.payment_method == payment_method)
                if start_date:
                    query = query.filter(Payment.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
                if end_date:
                    query = query.filter(Payment.created_at <= datetime.strptime(end_date, '%Y-%m-%d'))
                
                # Order by creation date (newest first)
                query = query.order_by(Payment.created_at.desc())
                
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
                payments_ns.abort(500, message=str(e))

        @payments_ns.doc('create_payment', security='Bearer')
        @payments_ns.expect(payment_create_model)
        @payments_ns.marshal_with(payment_model)
        @token_required
        def post(self, current_user):
            """Create a new payment"""
            try:
                data = request.get_json()
                
                # Create payment
                payment = Payment(
                    user_id=current_user.id,
                    amount=data['amount'],
                    currency=data.get('currency', 'USD'),
                    payment_method=data['payment_method'],
                    transaction_id=data.get('transaction_id'),
                    description=data.get('description'),
                    payment_metadata=data.get('payment_metadata'),
                    status='pending'
                )
                
                db.session.add(payment)
                db.session.commit()
                return payment
            except Exception as e:
                db.session.rollback()
                payments_ns.abort(500, message=str(e))

    @payments_ns.route('/<int:payment_id>')
    @payments_ns.param('payment_id', 'The payment identifier')
    class PaymentResource(Resource):
        @payments_ns.doc('get_payment', security='Bearer')
        @payments_ns.marshal_with(payment_model)
        @token_required
        def get(self, current_user, payment_id):
            """Get a payment by ID"""
            payment = Payment.query.get_or_404(payment_id)
            if payment.user_id != current_user.id:
                payments_ns.abort(403, "Access denied")
            return payment

        @payments_ns.doc('update_payment', security='Bearer')
        @payments_ns.expect(payment_update_model)
        @payments_ns.marshal_with(payment_model)
        @token_required
        def put(self, current_user, payment_id):
            """Update a payment"""
            payment = Payment.query.get_or_404(payment_id)
            if payment.user_id != current_user.id:
                payments_ns.abort(403, "Access denied")
                
            try:
                data = request.get_json()
                
                if 'status' in data:
                    payment.update_status(data['status'])
                if 'description' in data:
                    payment.description = data['description']
                if 'payment_metadata' in data:
                    payment.payment_metadata = data['payment_metadata']
                
                db.session.commit()
                return payment
            except ValueError as e:
                db.session.rollback()
                payments_ns.abort(400, message=str(e))
            except Exception as e:
                db.session.rollback()
                payments_ns.abort(500, message=str(e))

        @payments_ns.doc('delete_payment', security='Bearer')
        @token_required
        def delete(self, current_user, payment_id):
            """Delete a payment"""
            payment = Payment.query.get_or_404(payment_id)
            if payment.user_id != current_user.id:
                payments_ns.abort(403, "Access denied")
                
            try:
                db.session.delete(payment)
                db.session.commit()
                return '', 204
            except Exception as e:
                db.session.rollback()
                payments_ns.abort(500, message=str(e)) 