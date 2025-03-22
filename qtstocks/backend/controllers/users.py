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
        @users_ns.marshal_list_with(user_model)
        @token_required
        @admin_required
        def get(self, current_user):
            """List all users sorted by email"""
            return User.query.order_by(User.email.asc()).all()

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
                user.set_admin_status(not user.is_admin, current_user)
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
                user.set_active_status(not user.is_active, current_user)
                db.session.commit()
                return user
            except ValueError as e:
                users_ns.abort(400, str(e)) 