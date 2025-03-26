from flask import jsonify, request
from models import User, db, UserSettings
from extensions import ma
from datetime import datetime, timezone
from functools import wraps
from flask_restx import Resource, fields

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = kwargs.get('current_user')
        if not current_user or not current_user.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def init_user_routes(app, token_required, users_ns):
    # Define models for Swagger documentation
    user_model = users_ns.model('User', {
        'id': fields.Integer(readonly=True, description='User ID'),
        'email': fields.String(required=True, description='User email'),
        'name': fields.String(description='User name'),
        'is_admin': fields.Boolean(description='Admin status'),
        'is_active': fields.Boolean(description='Active status'),
        'is_google_user': fields.Boolean(description='Google user status'),
        'created_at': fields.DateTime(readonly=True, description='Account creation date', dt_format='iso8601'),
        'last_login': fields.DateTime(description='Last login date', dt_format='iso8601')
    })

    paginated_user_model = users_ns.model('PaginatedUser', {
        'items': fields.List(fields.Nested(user_model), description='List of users'),
        'total': fields.Integer(description='Total number of users'),
        'pages': fields.Integer(description='Total number of pages'),
        'current_page': fields.Integer(description='Current page number'),
        'has_next': fields.Boolean(description='Whether there is a next page'),
        'has_prev': fields.Boolean(description='Whether there is a previous page')
    })

    user_update_model = users_ns.model('UserUpdate', {
        'email': fields.String(description='User email'),
        'name': fields.String(description='User name'),
        'is_admin': fields.Boolean(description='Admin status'),
        'is_active': fields.Boolean(description='Active status'),
        'password': fields.String(description='New password')
    })

    # Define parser for user list endpoint
    user_list_parser = users_ns.parser()
    user_list_parser.add_argument('page', type=int, location='args', help='Page number')
    user_list_parser.add_argument('per_page', type=int, location='args', help='Items per page')
    user_list_parser.add_argument('search', type=str, location='args', help='Search term for username, email, or name')
    user_list_parser.add_argument('is_active', type=bool, location='args', help='Filter by active status')
    user_list_parser.add_argument('is_admin', type=bool, location='args', help='Filter by admin status')
    user_list_parser.add_argument('sort_by', type=str, location='args', required=False,
        choices=['id', 'username', 'name', 'email', 'created_at', 'updated_at', 'last_login', 'is_active', 'is_admin'], 
        help='Field to sort by (defaults to created_at)')
    user_list_parser.add_argument('sort_direction', type=str, location='args', 
        choices=['asc', 'desc'], help='Sort direction (asc or desc)')

    @users_ns.route('')
    class UserList(Resource):
        @users_ns.doc('list_users', security='bearer')
        @users_ns.expect(user_list_parser)
        @users_ns.marshal_with(paginated_user_model)
        @token_required
        def get(self, current_user):
            """List all users with pagination, filtering, and sorting"""
            if not current_user.is_admin:
                users_ns.abort(403, message="Only admin users can list all users")
            
            # Parse query parameters
            args = user_list_parser.parse_args()
            page = args.get('page', 1)
            per_page = args.get('per_page', 10)
            search = args.get('search')
            is_active = args.get('is_active')
            is_admin = args.get('is_admin')
            sort_by = args.get('sort_by', 'created_at')  # Default sort by created_at
            sort_direction = args.get('sort_direction', 'asc')  # Default ascending order
            
            # Handle empty string for sort_by
            if sort_by == '':
                sort_by = 'created_at'
            
            # Validate sort parameters
            valid_sort_fields = ['id', 'username', 'email', 'name', 'is_admin', 'is_active', 'is_google_user', 
                               'budget', 'created_at', 'updated_at', 'last_login']
            if sort_by not in valid_sort_fields:
                users_ns.abort(400, message=f"Invalid sort field. Must be one of: {', '.join(valid_sort_fields)}")
            
            if sort_direction not in ['asc', 'desc']:
                users_ns.abort(400, message="Invalid sort direction. Must be 'asc' or 'desc'")
            
            # Build query
            query = User.query
            
            # Apply filters
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    db.or_(
                        User.username.ilike(search_term),
                        User.email.ilike(search_term),
                        User.name.ilike(search_term)
                    )
                )
            
            if is_active is not None:
                query = query.filter(User.is_active == is_active)
            
            if is_admin is not None:
                query = query.filter(User.is_admin == is_admin)
            
            # Apply sorting
            sort_column = getattr(User, sort_by)
            if sort_direction == 'desc':
                sort_column = sort_column.desc()
            query = query.order_by(sort_column)
            
            # Execute query with pagination
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            users = pagination.items
            
            return {
                'items': [user.to_dict() for user in users],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }

    @users_ns.route('/<int:user_id>')
    @users_ns.param('user_id', 'The user identifier')
    class UserResource(Resource):
        @users_ns.doc('get_user', security='Bearer')
        @users_ns.marshal_with(user_model)
        @token_required
        @admin_required
        def get(self, current_user, user_id):
            """Get a user by ID"""
            return User.query.get_or_404(user_id)

        @users_ns.doc('update_user', security='Bearer')
        @users_ns.expect(user_update_model)
        @users_ns.marshal_with(user_model)
        @token_required
        @admin_required
        def put(self, current_user, user_id):
            """Update a user"""
            user = User.query.get_or_404(user_id)
            data = request.get_json()

            if 'email' in data:
                user.email = data['email']
            if 'name' in data:
                user.name = data['name']
            if 'is_admin' in data:
                try:
                    user.set_admin_status(data['is_admin'], current_user)
                except ValueError as e:
                    users_ns.abort(400, str(e))
            if 'is_active' in data:
                try:
                    user.set_active_status(data['is_active'], current_user)
                except ValueError as e:
                    users_ns.abort(400, str(e))
            if 'password' in data:
                user.set_password(data['password'])

            db.session.commit()
            return user

        @users_ns.doc('delete_user', security='Bearer')
        @token_required
        @admin_required
        def delete(self, current_user, user_id):
            """Delete a user"""
            user = User.query.get_or_404(user_id)
            
            # Prevent admin from deleting themselves
            if user.id == current_user.id:
                users_ns.abort(400, "Cannot delete your own admin account")
                
            db.session.delete(user)
            db.session.commit()
            return '', 204

    @users_ns.route('/<int:user_id>/toggle_admin')
    @users_ns.param('user_id', 'The user identifier')
    class UserToggleAdmin(Resource):
        @users_ns.doc('toggle_admin', security='Bearer')
        @users_ns.marshal_with(user_model)
        @token_required
        @admin_required
        def post(self, current_user, user_id):
            """Toggle admin status for a user"""
            user = User.query.get_or_404(user_id)
            
            try:
                user.toggle_admin_status(current_user)
                db.session.commit()
                return user
            except ValueError as e:
                users_ns.abort(400, str(e))

    @users_ns.route('/<int:user_id>/toggle_active')
    @users_ns.param('user_id', 'The user identifier')
    class UserToggleActive(Resource):
        @users_ns.doc('toggle_active', security='Bearer')
        @users_ns.marshal_with(user_model)
        @token_required
        @admin_required
        def post(self, current_user, user_id):
            """Toggle active status for a user"""
            user = User.query.get_or_404(user_id)
            
            try:
                user.toggle_active_status(current_user)
                db.session.commit()
                return user
            except ValueError as e:
                users_ns.abort(400, str(e))

    @users_ns.route('/<int:user_id>/budget')
    @users_ns.param('user_id', 'The user identifier')
    class UserBudget(Resource):
        @users_ns.doc('update_user_budget', security='Bearer')
        @users_ns.expect(users_ns.model('BudgetUpdate', {
            'amount': fields.Float(required=True, description='Amount to add (positive) or subtract (negative) from budget'),
            'reason': fields.String(required=True, description='Reason for the budget modification')
        }))
        @users_ns.marshal_with(user_model)
        @token_required
        def post(self, current_user, user_id):
            """Update a user's budget (admin only)"""
            if not current_user.is_admin:
                users_ns.abort(403, "Only admin users can modify budgets")
                
            target_user = User.query.get_or_404(user_id)
            
            try:
                data = request.get_json()
                amount = data.get('amount')
                reason = data.get('reason')
                
                if amount is None:
                    users_ns.abort(400, "Amount is required")
                if not reason:
                    users_ns.abort(400, "Reason is required")
                
                # Update user's budget
                target_user.budget += amount
                
                # Log the budget change in user settings
                budget_history = UserSettings.query.filter_by(
                    user_id=target_user.id,
                    setting_key='budget_history'
                ).first()
                
                if not budget_history:
                    budget_history = UserSettings(
                        user_id=target_user.id,
                        setting_key='budget_history',
                        setting_value=[]
                    )
                    db.session.add(budget_history)
                
                history_entry = {
                    'amount': amount,
                    'reason': reason,
                    'modified_by': current_user.id,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'new_balance': target_user.budget
                }
                
                budget_history.setting_value.append(history_entry)
                db.session.commit()
                
                return target_user
            except Exception as e:
                db.session.rollback()
                users_ns.abort(500, message=str(e))

        @users_ns.doc('get_user_budget_history', security='Bearer')
        @users_ns.param('page', 'Page number (1-based)', type=int, default=1)
        @users_ns.param('per_page', 'Items per page', type=int, default=10)
        @token_required
        def get(self, current_user, user_id):
            """Get user's budget modification history (admin only)"""
            if not current_user.is_admin:
                users_ns.abort(403, "Only admin users can view budget history")
                
            target_user = User.query.get_or_404(user_id)
            
            try:
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 10, type=int)
                
                # Get budget history from user settings
                budget_history = UserSettings.query.filter_by(
                    user_id=target_user.id,
                    setting_key='budget_history'
                ).first()
                
                if not budget_history:
                    return {
                        'items': [],
                        'total': 0,
                        'pages': 0,
                        'current_page': page,
                        'has_next': False,
                        'has_prev': False
                    }
                
                # Sort history by timestamp (newest first)
                history = sorted(
                    budget_history.setting_value,
                    key=lambda x: x['timestamp'],
                    reverse=True
                )
                
                # Paginate the history
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                paginated_history = history[start_idx:end_idx]
                
                return {
                    'items': paginated_history,
                    'total': len(history),
                    'pages': (len(history) + per_page - 1) // per_page,
                    'current_page': page,
                    'has_next': end_idx < len(history),
                    'has_prev': page > 1
                }
            except Exception as e:
                users_ns.abort(500, message=str(e)) 