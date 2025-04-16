from flask import Blueprint, jsonify, request
from models import db, Student, User
from resources.validations import *

from sqlalchemy import or_


student_bp = Blueprint('student_bp', __name__)



@student_bp.route('/', methods=["GET"])
def get_students():
    # filters
    search_data = request.args.get("search_data", type=str)
    page = request.args.get("page", default=1, type=int)
    page_size = request.args.get("page_size", default=10, type=int)
    section_id = request.args.get("section_id", type=int)
    tutorial_group_id = request.args.get("tutorial_group_id", type=int)
    lab_group_id = request.args.get("lab_group_id", type=int)
    status = request.args.get("status", type=str)
    
    students = Student.query
    
    if search_data:
        search_data = search_data.strip()
        try:
            search_id = int(search_data)
            students = students.filter(Student.id == search_id)
        except ValueError:
            students = students.filter(or_(
                Student.first_name.ilike(f"%{search_data}%"),
                Student.last_name.ilike(f"%{search_data}%"),
            ))        
    if section_id:
        students = students.filter(Student.section_id == section_id)
    if tutorial_group_id:
        students = students.filter(Student.tutorial_group_id == tutorial_group_id)
    if lab_group_id:
        students = students.filter(Student.lab_group_id == lab_group_id)
    if status:
        students = students.filter(Student.status == status)
    
    students = students.paginate(page=page, per_page=page_size)
    
    return jsonify({
        "success": True,
        "data": [student.to_dict() for student in students.items], 
        "pagination": {
            "totalItems": students.total,
            "currentPage": students.page,
            "pageSize": students.per_page,
            "totalPages": students.pages,
        }
    })

@student_bp.route('/', methods=["POST"])
def add_student():
    data = request.get_json()
    
    required_fields = [
        "email", "password", 
        "first_name", "last_name", 
        "birth_date", "nationality", "gender", 
        "disability", "phone_number", "observation", 
        "speciality_id", "section_id", 
        "tutorial_group_id", "lab_group_id",
        "status"
    ]
    
    error = run_validations([
        (validate_required_fields, [required_fields, data]),
        (validate_email_format, [data["email"]]),
        (validate_unique_field, [User, "email", data["email"], db]), # check for unique email in Users table
        (validate_password_length, [data["password"]]),
        (validate_date_format, data["birth_date"]),
    ])
    if error:
        return jsonify(error), 400
    
    validation_error = Student.validate_student(data, db)
    if validation_error:
        return jsonify(error), 400
    
    
    # give the student the role "Student" by default
    role = db.session.execute(db.select(Role).filter_by(role_name="Student")).first()
    data["role_id"] = role[0].role_id
    
    
    # create student
    new_user = User(email=data["email"], password_hash=User.hash_password(str(data["password"])), role_id=data["role_id"])
    db.session.add(new_user)
    db.session.commit()

    new_student = Student(
        user_id=new_user.user_id, 
        first_name=data['first_name'], 
        last_name=data['last_name'],
        birth_date=data['birth_date'],
        nationality=data['nationality'],
        gender=data['gender'],
        disability=data['disability'],
        phone_number=data['phone_number'],
        observation=data['observation'],
        speciality_id=data['speciality_id'],
        section_id=data['section_id'],
        tutorial_group_id=data['tutorial_group_id'],
        lab_group_id=data['lab_group_id'],
        status=data['status']
    )
    
    db.session.add(new_student)
    db.session.commit()
    
    return jsonify({
            "success": True,
            "message": "Student created successfully",
            "student": new_student.to_dict()
        }), 201
    
@student_bp.route('/<int:student_id>', methods=["GET"])
def get_student(student_id):
    student = Student.query.get(student_id)
    if student:
        return jsonify(student.to_dict())
    else:
        return jsonify({"error": "Student not found"}), 404

@student_bp.route('/<int:student_id>', methods=["PUT"])
def update_student(student_id):
    student = Student.query.get(student_id)
    
    if not student:
        return jsonify({
            "error": "Student not found"
        }), 404

    data = request.get_json()
    required_fields = [
        "first_name", "last_name", "birth_date", 
        "nationality", "gender", "disability",
        "phone_number", "observation", "status"
    ]
    
    error = run_validations([
        (validate_required_fields, [required_fields, data]),
        (validate_date_format, data["birth_date"])
    ])
    if error:
        return jsonify(error), 400
    

    # update student
    student.first_name = data['first_name']
    student.last_name=data['last_name']
    student.birth_date=data['birth_date']
    student.nationality=data['nationality']
    student.gender=data['gender']
    student.disability=data['disability']
    student.phone_number=data['phone_number']
    student.observation=data['observation']

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Student updated successfully",
        "student": student.to_dict()
    }), 200
  
@student_bp.route('/<int:student_id>', methods=["DELETE"])
def delete_student(student_id):
    student = Student.query.get(student_id)
    
    if not student:
        return jsonify({
            "error": "Student not found"
        }), 404
        
    user = User.query.get(student.user_id)
    db.session.delete(user)
    db.session.delete(student)
    db.session.commit()
    return jsonify({
        "success": True,
        "message": "student deleted sucessfully"
        }), 200

