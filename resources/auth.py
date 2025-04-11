import jwt
from datetime import datetime, timedelta
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
import bcrypt



SECRET_KEY = "JWT_SECRET_KEY"


def hash_password(password):
    salt = bcrypt.gensalt()
    hash_password = bcrypt.hashpw(password=password.encode(), salt=salt)
    return hash_password
    
def check_password(password):
        password = password.encode()
        check = bcrypt.checkpw(password=password, hashed_password=hash_password)
        if check:
            return True
        else:
            return False
        
        
        
        
# JWT authentication
def generate_token(user_id, role_id, expires_delta=timedelta(days=1)):
    payload = {
        'user_id': user_id,
        'role_id': role_id,
        'exp': datetime.utcnow() + expires_delta
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token):
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# 
def authenticate(permission_level_list):
    def wrapper(func):
        
        func()
        
    return wrapper 






# def role_required(min_permission_level):
#     def decorator(f):
#         @wraps(f)
#         def decorated(*args, **kwargs):
#             auth_result = token_required(lambda: None)()
#             if isinstance(auth_result, tuple) and auth_result[1] != 200:
#                 return auth_result
            
#             user = getattr(request, 'user')
#             if not user.role or user.role.permission_level < min_permission_level:
#                 return jsonify({'error': 'Insufficient permissions'}), 403
            
#             return f(*args, **kwargs)
#         return decorated
#     return decorator
