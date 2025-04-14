from validate_email import validate_email
import bcrypt
from datetime import datetime


def validate_required_fields(required_fields, data):
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    if missing_fields:
        return {"error": f"Missing data: {missing_fields}"}
    return None

def validate_unique_field(model, field_name, value, db, exclude_field_name=None, exclude_value=None):
        field = getattr(model, field_name)
        query = db.select(model).filter(field == value)
        if exclude_field_name and exclude_value:
            exclude_field = getattr(model, exclude_field_name)
            query = query.filter(exclude_field != exclude_value)
        existing = db.session.execute(query).first()
        if existing:
            return {"error": f"{field_name} already exists"}
        return None

def validate_positive_integer(value, field_name):
    try:
        if isinstance(value, float):
            return {"error": f"{field_name} must be a positive integer"}
        
        int_value = int(value)
        if int_value < 0:
            return {"error": f"{field_name} must be positive"}
        return None
    except (ValueError, TypeError):
        return {"error": f"{field_name} must be a positive integer"}

def validate_email_format(email):
    is_valid = validate_email(email)
    if not is_valid:
        return {"error": "Not valid email format"}
    return None

def validate_password_length(password):
    if len(str(password)) not in range(8, 32):
        return {"error": "Invalid password length"}
    return None

def validate_date_format(date, format='%d/%m/%Y'):
    try:
        datetime.strptime(date, format)
    except ValueError:
        return {"error": f"Invalid date format. Please use {format}"}
    return None

def run_validations(validations):
    for validate_func, args in validations:
        error = validate_func(*args)
        if error:
            return error  # Return the first error immediately
    return None  # No errors found


