from functools import wraps
from flask import jsonify, current_app, request
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
    verify_jwt_in_request
)
import jwt
from datetime import datetime, timedelta




# JWT token helper functions
def generate_token(user_id, role_id, expires_delta=timedelta(days=1)):
    """Generate JWT token for authentication"""
    payload = {
        'user_id': user_id,
        'role_id': role_id,
        'exp': datetime.utcnow() + expires_delta
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def decode_token(token):
    """Decode JWT token"""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Auth middleware decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401
        
        # Decode token
        data = decode_token(token)
        if not data:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Get user
        current_user = User.query.get(data['user_id'])
        if not current_user:
            return jsonify({'error': 'User not found'}), 401
        
        # Add user to request context
        setattr(request, 'user', current_user)
        setattr(request, 'user_id', current_user.user_id)
        setattr(request, 'role_id', current_user.role_id)
        
        return f(*args, **kwargs)
    
    return decorated

# Permission helper decorator
def role_required(min_permission_level):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_result = token_required(lambda: None)()
            if isinstance(auth_result, tuple) and auth_result[1] != 200:
                return auth_result
            
            user = getattr(request, 'user')
            if not user.role or user.role.permission_level < min_permission_level:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator

# @bp.route('/login', methods=['POST'])
# def login():
#     """
#     AUTHENTICATINGG a user and return a JWT token! 
#     """
#     data = requesst.get_json()
    
#     if not data or not data.get('email') or not data.get('password'):
#         return jsonify({'error': 'Email and password are required'}), 400
    
#     user = User.query.filter_by(email=data['email']).first()
#     if not user or not user.check_password(data['password']):
#         return jsonify({'error': 'Invalid email or password'}), 401
    
#     token = generate_token(user.user_id, user.role_id)
    
#     # Hnaya we sort info for the backend
#     user_info = {
#         'user_id': user.user_id,
#         'email': user.email,
#         'role': user.role.to_dict() if user.role else None
#     }
    
#     # Hnaya nzido njibo full info nta3 user depending on wether raho student or teacher
#     if hasattr(user, 'student') and user.student:
#         user_info['student'] = user.student.to_dict()
    
#     if hasattr(user, 'teacher') and user.teacher:
#         user_info['teacher'] = user.teacher.to_dict()
    
#     return jsonify({
#         'success': True,
#         'token': token,
#         'user': user_info
#     })

# @bp.route('/verify', methods=['GET'])
# @token_required
# def verify_token():
    """
    Verify a JWT token and return user info
    """
    user = getattr(request, 'user')
    
    # Get user info
    user_info = {
        'user_id': user.user_id,
        'email': user.email,
        'role': user.role.to_dict() if user.role else None
    }
    
    # Add student or teacher info if available
    if hasattr(user, 'student') and user.student:
        user_info['student'] = user.student.to_dict()
    
    if hasattr(user, 'teacher') and user.teacher:
        user_info['teacher'] = user.teacher.to_dict()
    
    return jsonify({
        'valid': True,
        'user': user_info
    })
    
    
    
    
    from models.user import User

    # New decorator: roles_required
    def roles_required(allowed_permission_levels):
        """
        Restrict access to users with specific permission levels.
        :param allowed_permission_levels: List of allowed permission levels.
        """
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                auth_result = token_required(lambda: None)()
                if isinstance(auth_result, tuple) and auth_result[1] != 200:
                    return auth_result
                
                user = getattr(request, 'user')
                if not user.role or user.role.permission_level not in allowed_permission_levels:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                return f(*args, **kwargs)
            return decorated
        return decorator