from flask import Blueprint, jsonify, request
from models import db, Staff, User, Role
from resources.validations import *

from sqlalchemy import or_

staff_bp = Blueprint('staff_bp', __name__)


@staff_bp.route('/', methods=["GET"])
def get_staffs():
    # filters
    search_data = request.args.get("search_data", type=str)
    page = request.args.get("page", default=1, type=int)
    page_size = request.args.get("page_size", default=10, type=int)
    role_id = request.args.get("role_id", type=int)
    email = request.args.get("email", type=str)

    staffs = Staff.query

    if search_data:
        search_data = search_data.strip()
        try:
            search_id = int(search_data)
            staffs = staffs.filter(Staff.staff_id == search_id)
        except ValueError:
            staffs = staffs.filter(or_(
                Staff.first_name.ilike(f"%{search_data}%"),
                Staff.last_name.ilike(f"%{search_data}%"),
            ))
    if role_id:
        staffs = staffs.join(User).filter(User.role_id == role_id)
    if email:
        staffs = staffs.join(User).filter(User.email.ilike(f"%{email}%"))

    staffs = staffs.paginate(page=page, per_page=page_size)

    return jsonify({
        "success": True,
        "data": [staff.to_dict() for staff in staffs.items],
        "pagination": {
            "totalItems": staffs.total,
            "currentPage": staffs.page,
            "pageSize": staffs.per_page,
            "totalPages": staffs.pages,
        }
    }), 200

@staff_bp.route('/<int:staff_id>', methods=["GET"])
def get_staff(staff_id):
    staff = Staff.query.get(staff_id)
    if not staff:
        return jsonify({"error": "Staff not found"}), 404

    return jsonify({
        "success": True,
        "data": staff.to_dict()
    }), 200

@staff_bp.route('/', methods=["POST"])
def add_staff():
    data = request.get_json()

    required_fields = ["email", "password", "first_name", "last_name", "grade"]
    error = run_validations([
        (validate_required_fields, [required_fields, data]),
        (validate_email_format, [data["email"]]),
        (validate_unique_field, [User, "email", data["email"], db]),
        (validate_password_length, [data["password"]])
    ])
    if error:
        return jsonify(error), 400

    # Assign the "Admin" role by default
    role = db.session.execute(db.select(Role).filter_by(role_name="Admin")).first()
    data["role_id"] = role[0].role_id

    # Create the user
    new_user = User(
        email=data["email"],
        hashed_password=User.hash_password(data["password"]),
        role_id=data["role_id"]
    )
    db.session.add(new_user)
    db.session.commit()

    # Create the staff
    new_staff = Staff(
        user_id=new_user.user_id,
        first_name=data["first_name"],
        last_name=data["last_name"],
        grade=data["grade"]
    )
    db.session.add(new_staff)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Staff created successfully",
        "staff": new_staff.to_dict()
    }), 201

@staff_bp.route('/<int:staff_id>', methods=["PUT"])
def update_staff(staff_id):
    staff = Staff.query.get(staff_id)
    if not staff:
        return jsonify({"error": "Staff not found"}), 404

    data = request.get_json()

    required_fields = ["first_name", "last_name", "grade"]
    error = run_validations([
        (validate_required_fields, [required_fields, data])
    ])
    if error:
        return jsonify(error), 400

    # Update staff
    staff.first_name = data["first_name"]
    staff.last_name = data["last_name"]
    staff.grade = data["grade"]
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Staff updated successfully",
        "staff": staff.to_dict()
    }), 200

@staff_bp.route('/<int:staff_id>', methods=["DELETE"])
def delete_staff(staff_id):
    staff = Staff.query.get(staff_id)
    if not staff:
        return jsonify({"error": "Staff not found"}), 404

    # delete the associated user account
    user = User.query.get(staff.user_id)
    db.session.delete(user)
    
    db.session.delete(staff)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Staff deleted successfully"
    }), 200
    