from flask import jsonify, request
from models import User, db
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
        'created_at': fields.DateTime(readonly=True, description='Account creation date'),
        'last_login': fields.DateTime(description='Last login date')
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

    @users_ns.route('')
    class UserList(Resource):
        @users_ns.doc('list_users', security='Bearer')
        @users_ns.param('page', 'Page number (1-based)', type=int, default=1)
        @users_ns.param('per_page', 'Items per page', type=int, default=10)
        @users_ns.param('search', 'Search by email or name (partial match)', type=str)
        @users_ns.param('is_active', 'Filter by active status', type=bool)
        @users_ns.param('is_admin', 'Filter by admin status', type=bool)
        @users_ns.param('is_google_user', 'Filter by Google user status', type=bool)
        @users_ns.marshal_with(paginated_user_model)
        @token_required
        @admin_required
        def get(self, current_user):
            """List all users with pagination, search and filters"""
            try:
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 10, type=int)
                search = request.args.get('search', '').strip()
                is_active = request.args.get('is_active', type=bool)
                is_admin = request.args.get('is_admin', type=bool)
                is_google_user = request.args.get('is_google_user', type=bool)
                
                # Build query
                query = User.query
                
                # Apply search filter if provided
                if search:
                    search_term = f"%{search}%"
                    query = query.filter(
                        db.or_(
                            User.email.ilike(search_term),
                            User.name.ilike(search_term)
                        )
                    )
                
                # Apply filters if provided
                if is_active is not None:
                    query = query.filter(User.is_active == is_active)
                if is_admin is not None:
                    query = query.filter(User.is_admin == is_admin)
                if is_google_user is not None:
                    query = query.filter(User.google_id.isnot(None) == is_google_user)
                
                # Query with pagination
                # Sort by email in ascending order
                query = query.order_by(User.email.asc())
                pagination = query.paginate(
                    page=page,
                    per_page=per_page,
                    error_out=False
                )
                
                return {
                    'items': pagination.items,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'current_page': page,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            except Exception as e:
                users_ns.abort(500, message=str(e))

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