from flask import Blueprint, jsonify, request
from models.staff import Staff
from models import db
from resources.validations import *

staff_bp = Blueprint('staff_bp', __name__)


@staff_bp.route('/', methods=["GET"])
def get_staffs():
    staffs = Staff.query.all()
    return jsonify([staff.to_dict() for staff in staffs])

@staff_bp.route('/<int:staff_id>', methods=["GET"])
def get_staff(staff_id):
    staff = Staff.query.get(staff_id)
    
    if not staff:
        return jsonify({
            "error": "Staff not found"
        }), 404

    return jsonify(staff.to_dict())

@staff_bp.route('/', methods=["POST"])
def add_staff():
    """
        REQUEST FORM:
        {
            "email": "example@gmail.com",
            "password": "12345678",
            "first_name": "test",
            "last_name": "example",
            "grade": "Doctorat",
        }
    """
    data = request.get_json()
    
    required_fields = ["email", "password", "first_name", "last_name", "grade"]
    error = validate_required_fields(required_fields, data)
    if error:
        return jsonify(error), 400
    
    
    error = run_validations([
        (validate_email_format, [data["email"]]),
        (validate_unique_field, [User, "email", data["email"], db]), # check for unique email in Users table
        (validate_password_length, [data["password"]]),
    ])
    if error:
        return jsonify(error), 400
    
    
    # give the staff the role "Admin" by default
    role = db.session.execute(db.select(Role).filter_by(role_name="Admin")).first()
    data["role_id"] = role[0].role_id  
    

    new_user = User(email=data["email"], hashed_password=hash_password(str(data["password"])), role_id=data["role_id"])
    db.session.add(new_user)
    db.session.commit()

    new_staff = Staff(
        user_id=new_user.user_id,
        first_name=data["first_name"],
        last_name=data["last_name"],
        grade=data["grade"]
    )
    db.session.add(new_staff)
    db.session.commit()
    
    return jsonify(new_staff.to_dict())

@staff_bp.route('/<int:staff_id>', methods=["PUT"])
def update_staff(staff_id):
    """
        REQUEST FORM:
        {
            "first_name": "test",
            "last_name": "example",
            "grade": "Doctorat",
        }
    """
    
    staff = Staff.query.get(staff_id)
    if not staff:
        return jsonify({
            "error": "Staff not found"
        }), 404
    
    data = request.get_json()
    
    required_fields = ["first_name", "last_name", "grade"]
    error = validate_required_fields(required_fields, data)
    if error:
        return jsonify(error), 400
    
    staff.first_name=data["first_name"]
    staff.last_name=data["last_name"]
    staff.grade=data["grade"]
    
    db.session.commit()
    
    return jsonify({
        "message": "Updated succesfully"
    }), 200

@staff_bp.route('/<int:staff_id>', methods=["DELETE"])
def delete_staff(staff_id):
    staff = Staff.query.get(staff_id)
    
    if not staff:
        return jsonify({
            "error": "Staff not found"
        }), 404
    
    db.session.delete(staff)
    db.session.commit()
    
    return jsonify({"message": "staff deleted sucessfully"}), 200
    