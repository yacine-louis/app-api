from flask import Blueprint, jsonify, request
from models.student import Student
from models import db
from resources.validations import *

student_bp = Blueprint('student_bp', __name__)


@student_bp.route('/', methods=["GET"])
def get_students():
    students = Student.query.all()
    return jsonify([student.to_dict() for student in students])

@student_bp.route('/<int:student_id>', methods=["GET"])
def get_student(student_id):
    student = Student.query.get(student_id)
    if student:
        return jsonify(student.to_dict())
    else:
        return jsonify({"error": "Student not found"}), 404
    
    #get students by speciality and section:
@student_bp.route('/students/speciality/<int:speciality_id>/section/<int:section_id>', methods = ["GET"])
def get_students_v2(speciality_id,section_id):
    students = db.session.query(Student).filter(
        Student.speciality_id == speciality_id,
        Student.section_id  == section_id
    ).all()
    if not students:
        return jsonify({"error" : "no students found for given speciality and section"}),404
    return jsonify([student.to_dict() for student in students]),200


@student_bp.route('/', methods=["POST"])
def add_student():
    """
        REQUEST FORM:
        {
            "email": "example@gmail.com",
            "password": "12345678"
            "matricule": 02323245326,
            "first_name": "test",
            "last_name": "example",
            'birth_date': "01/01/2025",
            'nationality': "Algerian",
            'gender': "Male",
            'disability': false,
            'phone_number': "0550505050",
            'observation': "new student",
            'speciality_id': 3,
            'section_id': 4,
            'tutorial_group_id': 1,
            'lab_group_id': 2
        }
    """
    data = request.get_json()
    required_fields = [
        "email", "password", 
        "matricule", "first_name", "last_name", 
        "birth_date", "nationality", "gender", 
        "disability", "phone_number", "observation", 
        "speciality_id", "section_id", "tutorial_group_id", "lab_group_id"
    ]
    error = validate_required_fields(required_fields, data)
    if error:
        return jsonify(error), 400

    
    
    error = run_validations([
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
    new_user = User(email=data["email"], hashed_password=hash_password(str(data["password"])), role_id=data["role_id"])
    db.session.add(new_user)
    db.session.commit()

    new_student = Student(
        user_id=new_user.user_id, 
        matricule=data['matricule'], 
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
        lab_group_id=data['lab_group_id']
    )
    
    db.session.add(new_student)
    db.session.commit()
    return jsonify(new_student.to_dict())
    
@student_bp.route('/<int:student_id>', methods=["DELETE"])
def delete_student(student_id):
    student = Student.query.get(student_id)
    
    if not student:
        return jsonify({
            "error": "Student not found"
        }), 404
    
    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "student deleted sucessfully"}), 200
    
@student_bp.route('/<int:student_id>', methods=["PUT"])
def update_student(student_id):
    """
        REQUEST FORM:
        {
            "matricule": 02323245326,
            "first_name": "test",
            "last_name": "example",
            'birth_date': "01/01/2025",
            'nationality': "Algerian",
            'gender': "Male",
            'disability': false,
            'phone_number': "0550505050",
            'observation': "new student",
        }
    """
    student = Student.query.get(student_id)
    
    if not student:
        return jsonify({
            "error": "Student not found"
        }), 404

    data = request.get_json()
    required_fields = [
        "matricule", "first_name", "last_name", 
        "birth_date", "nationality", "gender", 
        "disability", "phone_number", "observation"
    ]
    error = validate_required_fields(required_fields, data)
    if error:
        return jsonify(error), 400
    
    error = validate_date_format(data["birth_date"])
    if error:
        return jsonify(error), 400
    

    student.matricule = data['matricule']
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
        "message": "Updated succesfully"
    }), 200

