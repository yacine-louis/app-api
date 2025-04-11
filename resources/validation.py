from flask import jsonify
from validate_email import validate_email

def check_required_fields(required_fields, data):
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({
                "error": "Missing data",
            }), 400
    return None

def check_unique_field(model, field_name, value, db, exclude_field_name=None, exclude_value=None):
    field = getattr(model, field_name)
    query = db.select(model).filter(field == value)
    
    if exclude_field_name and exclude_value:
        exclude_field = getattr(model, exclude_field_name)
        query = query.filter(exclude_field != exclude_value)

    existing = db.session.execute(query).first()
    if existing:
        return jsonify({
            "error": f"{field_name} already exist"
        }), 400
    return None

def validate_positive_integer(value, field_name):
    try:
        if isinstance(value, float):
            return jsonify({
                "error": f"{field_name} must be a positive integer"
            }), 400
        
        
        int_value = int(value)
        if int_value < 0:
            return jsonify({
                "error": f"{field_name} must be positive"
            }), 400
        return None
    except (ValueError, TypeError):
        return jsonify({
            "error": f"{field_name} must be a positive integer"
        }), 400 

def validate_email_format(email):
    is_valid = validate_email(email)
    if not is_valid:
        return jsonify({
            "error": "Not valid email format",
        }), 400 
    return None

def validate_password_length(password):
    if len(str(password)) not in range(8, 32):
        return jsonify({
            "error": "Invalid password length"
        }), 400
    return None

def run_validations(validations):
    for validate_func, args in validations:
        error = validate_func(*args)
        if error:
            return error
    return None

























                


# @app.route('/users', methods=["POST"])
# def add_user():
#     data = request.get_json()
    
#     required_fields = ["email", "password", "role_id"]
#     error = check_required_fields(required_fields, data)
#     if error:
#         return error
    
#     error = User.validate_user(data, db)
#     if error:
#         return error
        
#     # create user
#     new_user = User(email=data["email"], hashed_password=hash_password(str(data["password"])), role_id=data["role_id"])
#     db.session.add(new_user)
#     db.session.commit()
    
#     return jsonify(new_user.to_dict()), 201
