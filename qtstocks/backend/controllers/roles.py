from flask import request
from flask_restx import Resource, Namespace, fields
from models import Role, Permission, User, Product, db
from utils.auth import admin_required

def init_role_routes(app, token_required, roles_ns):
    # Swagger documentation models
    permission_model = roles_ns.model('Permission', {
        'id': fields.Integer(readonly=True),
        'name': fields.String(required=True),
        'description': fields.String,
        'resource': fields.String(required=True),
        'action': fields.String(required=True),
        'is_active': fields.Boolean,
        'created_at': fields.DateTime(readonly=True),
        'updated_at': fields.DateTime(readonly=True)
    })
    
    role_model = roles_ns.model('Role', {
        'id': fields.Integer(readonly=True),
        'name': fields.String(required=True),
        'description': fields.String,
        'is_active': fields.Boolean,
        'permissions': fields.List(fields.Nested(permission_model)),
        'created_at': fields.DateTime(readonly=True),
        'updated_at': fields.DateTime(readonly=True)
    })
    
    role_create_model = roles_ns.model('RoleCreate', {
        'name': fields.String(required=True),
        'description': fields.String,
        'permission_ids': fields.List(fields.Integer, required=True)
    })
    
    role_update_model = roles_ns.model('RoleUpdate', {
        'name': fields.String,
        'description': fields.String,
        'is_active': fields.Boolean,
        'permission_ids': fields.List(fields.Integer)
    })
    
    # Add product-role relationship models
    product_role_model = roles_ns.model('ProductRole', {
        'id': fields.Integer(readonly=True),
        'name': fields.String(required=True),
        'description': fields.String,
        'is_active': fields.Boolean,
        'permissions': fields.List(fields.Nested(permission_model)),
        'created_at': fields.DateTime(readonly=True),
        'updated_at': fields.DateTime(readonly=True)
    })
    
    product_role_update_model = roles_ns.model('ProductRoleUpdate', {
        'role_ids': fields.List(fields.Integer, required=True)
    })
    
    @roles_ns.route('/roles')
    class RoleList(Resource):
        @roles_ns.doc('list_roles')
        @roles_ns.marshal_list_with(role_model)
        @token_required
        @admin_required
        def get(self):
            """List all roles"""
            return Role.query.all()
        
        @roles_ns.doc('create_role')
        @roles_ns.expect(role_create_model)
        @roles_ns.marshal_with(role_model, code=201)
        @token_required
        @admin_required
        def post(self):
            """Create a new role"""
            data = request.get_json()
            
            # Check if role name already exists
            if Role.query.filter_by(name=data['name']).first():
                roles_ns.abort(400, f"Role with name '{data['name']}' already exists")
            
            # Get permissions
            permissions = Permission.query.filter(Permission.id.in_(data['permission_ids'])).all()
            if len(permissions) != len(data['permission_ids']):
                roles_ns.abort(400, "One or more permission IDs are invalid")
            
            # Create role
            role = Role(
                name=data['name'],
                description=data.get('description'),
                permissions=permissions
            )
            
            db.session.add(role)
            db.session.commit()
            
            return role, 201
    
    @roles_ns.route('/roles/<int:id>')
    @roles_ns.param('id', 'The role identifier')
    class RoleResource(Resource):
        @roles_ns.doc('get_role')
        @roles_ns.marshal_with(role_model)
        @token_required
        @admin_required
        def get(self, id):
            """Get a role by id"""
            role = Role.query.get_or_404(id)
            return role
        
        @roles_ns.doc('update_role')
        @roles_ns.expect(role_update_model)
        @roles_ns.marshal_with(role_model)
        @token_required
        @admin_required
        def put(self, id):
            """Update a role"""
            role = Role.query.get_or_404(id)
            data = request.get_json()
            
            if 'name' in data and data['name'] != role.name:
                if Role.query.filter_by(name=data['name']).first():
                    roles_ns.abort(400, f"Role with name '{data['name']}' already exists")
                role.name = data['name']
            
            if 'description' in data:
                role.description = data['description']
            
            if 'is_active' in data:
                role.is_active = data['is_active']
            
            if 'permission_ids' in data:
                permissions = Permission.query.filter(Permission.id.in_(data['permission_ids'])).all()
                if len(permissions) != len(data['permission_ids']):
                    roles_ns.abort(400, "One or more permission IDs are invalid")
                role.permissions = permissions
            
            db.session.commit()
            return role
        
        @roles_ns.doc('delete_role')
        @roles_ns.response(204, 'Role deleted')
        @token_required
        @admin_required
        def delete(self, id):
            """Delete a role"""
            role = Role.query.get_or_404(id)
            
            # Check if role has any users
            if role.users.count() > 0:
                roles_ns.abort(400, "Cannot delete role with associated users")
            
            db.session.delete(role)
            db.session.commit()
            return '', 204
    
    @roles_ns.route('/permissions')
    class PermissionList(Resource):
        @roles_ns.doc('list_permissions')
        @roles_ns.marshal_list_with(permission_model)
        @token_required
        @admin_required
        def get(self):
            """List all permissions"""
            return Permission.query.all()
        
        @roles_ns.doc('create_permission')
        @roles_ns.expect(permission_model)
        @roles_ns.marshal_with(permission_model, code=201)
        @token_required
        @admin_required
        def post(self):
            """Create a new permission"""
            data = request.get_json()
            
            # Check if permission name already exists
            if Permission.query.filter_by(name=data['name']).first():
                roles_ns.abort(400, f"Permission with name '{data['name']}' already exists")
            
            permission = Permission(**data)
            db.session.add(permission)
            db.session.commit()
            
            return permission, 201
    
    @roles_ns.route('/permissions/<int:id>')
    @roles_ns.param('id', 'The permission identifier')
    class PermissionResource(Resource):
        @roles_ns.doc('get_permission')
        @roles_ns.marshal_with(permission_model)
        @token_required
        @admin_required
        def get(self, id):
            """Get a permission by id"""
            permission = Permission.query.get_or_404(id)
            return permission
        
        @roles_ns.doc('update_permission')
        @roles_ns.expect(permission_model)
        @roles_ns.marshal_with(permission_model)
        @token_required
        @admin_required
        def put(self, id):
            """Update a permission"""
            permission = Permission.query.get_or_404(id)
            data = request.get_json()
            
            if 'name' in data and data['name'] != permission.name:
                if Permission.query.filter_by(name=data['name']).first():
                    roles_ns.abort(400, f"Permission with name '{data['name']}' already exists")
                permission.name = data['name']
            
            for key, value in data.items():
                if hasattr(permission, key):
                    setattr(permission, key, value)
            
            db.session.commit()
            return permission
        
        @roles_ns.doc('delete_permission')
        @roles_ns.response(204, 'Permission deleted')
        @token_required
        @admin_required
        def delete(self, id):
            """Delete a permission"""
            permission = Permission.query.get_or_404(id)
            
            # Check if permission has any roles
            if permission.roles.count() > 0:
                roles_ns.abort(400, "Cannot delete permission with associated roles")
            
            db.session.delete(permission)
            db.session.commit()
            return '', 204
    
    @roles_ns.route('/users/<int:user_id>/roles')
    @roles_ns.param('user_id', 'The user identifier')
    class UserRoles(Resource):
        @roles_ns.doc('get_user_roles')
        @roles_ns.marshal_list_with(role_model)
        @token_required
        @admin_required
        def get(self, user_id):
            """Get all roles for a user"""
            user = User.query.get_or_404(user_id)
            return user.roles.all()
        
        @roles_ns.doc('assign_user_roles')
        @roles_ns.expect(roles_ns.model('UserRolesUpdate', {
            'role_ids': fields.List(fields.Integer, required=True)
        }))
        @roles_ns.response(204, 'Roles updated')
        @token_required
        @admin_required
        def put(self, user_id):
            """Assign roles to a user"""
            user = User.query.get_or_404(user_id)
            data = request.get_json()
            
            # Get roles
            roles = Role.query.filter(Role.id.in_(data['role_ids'])).all()
            if len(roles) != len(data['role_ids']):
                roles_ns.abort(400, "One or more role IDs are invalid")
            
            # Update user roles
            user.roles = roles
            db.session.commit()
            
            return '', 204
    
    @roles_ns.route('/products/<int:product_id>/roles')
    @roles_ns.param('product_id', 'The product identifier')
    class ProductRoles(Resource):
        @roles_ns.doc('get_product_roles')
        @roles_ns.marshal_list_with(role_model)
        @token_required
        @admin_required
        def get(self, product_id):
            """Get all roles for a product"""
            product = Product.query.get_or_404(product_id)
            return product.roles.all()
        
        @roles_ns.doc('assign_product_roles')
        @roles_ns.expect(product_role_update_model)
        @roles_ns.response(204, 'Roles updated')
        @token_required
        @admin_required
        def put(self, product_id):
            """Assign roles to a product"""
            product = Product.query.get_or_404(product_id)
            data = request.get_json()
            
            # Get roles
            roles = Role.query.filter(Role.id.in_(data['role_ids'])).all()
            if len(roles) != len(data['role_ids']):
                roles_ns.abort(400, "One or more role IDs are invalid")
            
            # Update product roles
            product.roles = roles
            db.session.commit()
            
            return '', 204
    
    @roles_ns.route('/users/<int:user_id>/product-roles')
    @roles_ns.param('user_id', 'The user identifier')
    class UserProductRoles(Resource):
        @roles_ns.doc('get_user_product_roles')
        @roles_ns.marshal_list_with(role_model)
        @token_required
        @admin_required
        def get(self, user_id):
            """Get all roles for a user through their active subscriptions"""
            user = User.query.get_or_404(user_id)
            
            # Get all active subscriptions
            active_subscriptions = user.subscriptions.filter_by(status='active').all()
            
            # Collect unique roles from all active subscriptions
            roles = set()
            for subscription in active_subscriptions:
                roles.update(subscription.get_user_roles())
            
            return list(roles)
    
    @roles_ns.route('/users/<int:user_id>/product-permissions')
    @roles_ns.param('user_id', 'The user identifier')
    class UserProductPermissions(Resource):
        @roles_ns.doc('get_user_product_permissions')
        @roles_ns.marshal_list_with(permission_model)
        @token_required
        @admin_required
        def get(self, user_id):
            """Get all permissions for a user through their active subscriptions"""
            user = User.query.get_or_404(user_id)
            
            # Get all active subscriptions
            active_subscriptions = user.subscriptions.filter_by(status='active').all()
            
            # Collect unique permissions from all active subscriptions' roles
            permissions = set()
            for subscription in active_subscriptions:
                for role in subscription.get_user_roles():
                    permissions.update(role.permissions)
            
            return list(permissions)
    
    @roles_ns.route('/users/<int:user_id>/check-permission')
    @roles_ns.param('user_id', 'The user identifier')
    class UserPermissionCheck(Resource):
        @roles_ns.doc('check_user_permission')
        @roles_ns.expect(roles_ns.model('PermissionCheck', {
            'resource': fields.String(required=True),
            'action': fields.String(required=True)
        }))
        @roles_ns.response(200, 'Permission check result')
        @token_required
        @admin_required
        def post(self, user_id):
            """Check if a user has a specific permission through their active subscriptions"""
            user = User.query.get_or_404(user_id)
            data = request.get_json()
            
            # Get all active subscriptions
            active_subscriptions = user.subscriptions.filter_by(status='active').all()
            
            # Check permissions through all active subscriptions
            for subscription in active_subscriptions:
                for role in subscription.get_user_roles():
                    for permission in role.permissions:
                        if permission.resource == data['resource'] and permission.action == data['action']:
                            return {'has_permission': True}
            
            return {'has_permission': False} 