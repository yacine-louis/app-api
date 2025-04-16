from flask import Blueprint, jsonify, request
from models import db, User, Teacher, TeacherSection, TeacherGroup, Role
from resources.validations import *

from sqlalchemy import or_

teacher_bp  = Blueprint('teacher_bp',__name__)

@teacher_bp.route('/', methods=["GET"])
def get_teachers():
    # filters
    search_data = request.args.get("search_data", type=str)
    page = request.args.get("page", default=1, type=int)
    page_size = request.args.get("page_size", default=10, type=int)
    section_id = request.args.get("section_id", type=int)
    tutorial_group_id = request.args.get("tutorial_group_id", type=int)
    lab_group_id = request.args.get("lab_group_id", type=int)
    
    teachers = Teacher.query
    
    if search_data:
        search_data = search_data.strip()
        try:
            search_id = int(search_data)
            teachers = teachers.filter(Teacher.teacher_id == search_id)
        except ValueError:
            teachers = teachers.filter(or_(
                Teacher.first_name.ilike(f"%{search_data}%"),
                Teacher.last_name.ilike(f"%{search_data}%"),
            ))
    if section_id:
        teachers = teachers.join(TeacherSection).filter(TeacherSection.section_id == section_id)
    if tutorial_group_id:
        teachers = teachers.join(TeacherGroup).filter(TeacherGroup.group_id == tutorial_group_id)
    if lab_group_id:
        teachers = teachers.join(TeacherGroup).filter(TeacherGroup.group_id == lab_group_id)
    
    teachers = teachers.paginate(page=page, per_page=page_size)
    
    
    return jsonify({
        "success": True,
        "data": [teacher.to_dict() for teacher in teachers.items], 
        "pagination": {
            "totalItems": teachers.total,
            "currentPage": teachers.page,
            "pageSize": teachers.per_page,
            "totalPages": teachers.pages,
        }
    })

@teacher_bp.route('/<int:teacher_id>',methods=["GET"])
def get_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({"error" : "no teacher found"}),404
    return jsonify(teacher.to_dict()),200

@teacher_bp.route('/', methods = ["POST"])
def add_teacher():
    data = request.get_json()
    
    required_fields = ["email", "password","first_name","last_name","grade"]
    error = run_validations([
        (validate_required_fields, [required_fields, data]),
        (validate_email_format, data["email"]),
        (validate_password_length, data["password"])
    ])
    if error:
        return jsonify(error), 400

    # give the teacher the role "Teacher" by default
    role = db.session.execute(db.select(Role).filter_by(role_name="Teacher")).first()
    data["role_id"] = role[0].role_id
    
    # create new user
    new_user = User(email=data["email"], password_hash=User.hash_password(str(data["password"])), role_id=data["role_id"])
    db.session.add(new_user)
    db.session.commit()
    
    new_teacher = Teacher(
        user_id=new_user.user_id,
        first_name=data["first_name"],
        last_name=data["last_name"],
        grade=data["grade"]
    )
    db.session.add(new_teacher)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Teacher created successfully",
        "teacher": new_teacher.to_dict()
    }), 201

@teacher_bp.route('/<int:teacher_id>', methods=["PUT"])
def update_teacher(teacher_id):
    
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({"error" : "teacher not found"}),404
    
    data = request.get_json()
    required_fields = ["first_name","last_name","grade"]
    
    error = run_validations([
        (validate_required_fields, [required_fields, data]),
    ])
    if error:
        return jsonify(error), 400
    
    # update teacher
    teacher.first_name = data["first_name"]
    teacher.last_name = data["last_name"]
    teacher.grade = data["grade"]
    
    db.session.commit()
    
    return jsonify({
            "success": True,
            "message": "Teacher updated successfully",
            "teacher": teacher.to_dict()
        }), 200

@teacher_bp.route('/teachers/<int:teacher_id>', methods=["DELETE"])
def delete_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({"error : teacher not found"}),400
    
    db.session.delete(teacher)
    db.session.commit()
    
    return jsonify({
        "success": True,
        "message": "teacher deleted sucessfully"
        }), 200

