from flask import Blueprint, jsonify, request
from models.teacher import Teacher
from models.user import User
from models import db
from resources.validations import *

teacher_bp  = Blueprint('teacher_bp',__name__)

@teacher_bp.route('/teachers', methods=["GET"])
def get_teachers():
    teachers = Teacher.query.all()
    if not teachers:
        return jsonify({"error" : "no teacher found"}),404
    return [teacher.to_dict() for teacher in teachers],200

@teacher_bp.route('/teachers/<int:teacher_id>',methods=["GET"])
def get_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({"error" : "no teacher found"}),404
    return jsonify(teacher.to_dict()),200
@teacher_bp.route('/teachers', methods = ["POST"])
def add_teacher():
    data = request.get_json()
    required_fields = ["user_id","first_name","last_name","grade"]
    error = run_validations(validate_required_fields(required_fields, data)
, validate_positive_integer(data["user_id"], "User id"))
    
    if error:
        return error
    user = User.query.get(data["user_id"])

    if not user:
        return jsonify({"error": "user not found"}),400
    
    teacher = Teacher(
        user_id=data["user_id"],
        first_name = data["first_name"],
        last_name = data["last_name"],
        grade = data["grade"]
    )
    db.session.add(teacher)
    db.session.commit()

    return jsonify({"message" : "teacher added sucessfully"}),200
    

@teacher_bp.route('/teachers/<int:teacher_id>', methods=["PUT"])
def update_teacher(teacher_id):
     
    teacher = Teacher.query.get(teacher_id)
     
    if not teacher:
        return jsonify({"error" : "teacher not found"}),400
    teacher_user_id = teacher.user_id
    data = request.get_json()
    required_fields = ["user_id","first_name","last_name","grade"]
    error = run_validations(validate_required_fields(required_fields, data)
, validate_positive_integer(data["user_id"], "User id"), validate_unique_field(Teacher,"user_id", data["user_id"], db,"user_id",teacher_user_id))
    if error:
        return error
     # if the updated teacher has a new user_id we gotta verifiy if it exists
    if data["user_id"] != teacher_user_id:
        user = User.query.get(data["user_id"])
        if not user:
            return jsonify({"error" : "user not found"}),400
    teacher.user_id=data["user_id"]
    teacher.first_name = data["first_name"]
    teacher.last_name = data["last_name"]
    teacher.grade = data["grade"]  
    db.session.commit()
    return jsonify({"message" : "teacher updated sucessfully"}),200

@teacher_bp.route('/teachers/<int:teacher_id>', methods=["DELETE"])
def delete_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({"error : teacher not found"}),400
    db.session.delete(teacher)
    db.session.commit()
    return jsonify({"message":"teacher deleted sucessfully"}),200


