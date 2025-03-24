from functools import wraps
from flask import request, jsonify
from flask_login import current_user
from models import User
import jwt
from config import Config

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            # Decode token
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            
            if not current_user:
                return jsonify({'message': 'User not found'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'message': 'Authentication required'}), 401
        
        if not current_user.is_admin:
            return jsonify({'message': 'Admin privileges required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function 