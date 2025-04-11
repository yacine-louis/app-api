from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from sqlalchemy import Column, Integer, String, MetaData, Table, TIMESTAMP, ForeignKey, Date, Text, Boolean

from sqlalchemy import select
from sqlalchemy.orm import relationship, Session, DeclarativeBase

from resources.auth import hash_password, check_password
from resources.validation import check_required_fields, check_unique_field, validate_positive_integer, validate_email_format, validate_password_length, run_validations

class Base(DeclarativeBase):
    __abstract__ = True
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

db = SQLAlchemy(model_class=Base)

# database config
DB_USER = 'root'
DB_PASSWORD = 'root'
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_SECHEMA_NAME = 'student_db'

# flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_SECHEMA_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# migrate database
migrate = Migrate(app, db)


# Define Table Classes
class Role(db.Model):
    __tablename__ = 'roles'
    
    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    role_name = db.Column(db.String(64), nullable=False)
    permission_level = db.Column(db.Integer, nullable=False)
    protected = db.Column(db.Boolean, default=False)
    
    users = db.relationship('User', backref='role', lazy=True)
    
    def to_dict(self):
        return {
            'role_id': self.role_id,
            'role_name': self.role_name,
            'permission_level': self.permission_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    hashed_password = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)
    
    teachers = db.relationship('Teacher', backref='user', lazy=True)
    students = db.relationship('Student', backref='user', lazy=True)
    staffs = db.relationship('Staff', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'email': self.email,
            'role_id': self.role_id,
            'hashed_password': self.hashed_password,
            'role': self.role.to_dict() if self.role else None, 
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
class Speciality(db.Model):
    __tablename__ = 'specialities'
    
    speciality_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(128), nullable=False, unique=True)
    education_level = db.Column(db.Integer, nullable=False)
    
    sections = db.relationship('Section', backref='speciality', lazy=True)
    students = db.relationship('Student', backref='speciality', lazy=True)
    
    def to_dict(self):
        return {
            'speciality_id': self.speciality_id,
            'name': self.name,
            'education_level': self.education_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Section(db.Model):
    __tablename__ = 'sections'
    
    section_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    speciality_id = db.Column(db.Integer, db.ForeignKey('specialities.speciality_id'), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    max_capacity = db.Column(db.Integer, nullable=False)
    
    groups = db.relationship('Group', backref='section', lazy=True)
    students = db.relationship('Student', backref='section', lazy=True)
    teacher_sections = db.relationship('TeacherSection', backref='section', lazy=True)
    
    def to_dict(self):
        return {
            'section_id': self.section_id,
            'speciality_id': self.speciality_id,
            'speciality': self.speciality.to_dict() if self.speciality else None,
            'name': self.name,
            'max_capacity': self.max_capacity,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    teacher_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    grade = db.Column(db.String(128), nullable=False)
    
    teacher_sections = db.relationship('TeacherSection', backref='teacher', lazy=True)
    teacher_groups = db.relationship('TeacherGroup', backref='teacher', lazy=True)
    
    def to_dict(self):
        return {
            'teacher_id': self.teacher_id,
            'user_id': self.user_id,
            'user': self.user.to_dict() if self.user else None,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'grade': self.grade,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Group(db.Model):
    __tablename__ = 'groups'
    
    group_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.section_id'), nullable=False)
    group_type = db.Column(db.String(64), nullable=False)
    group_name = db.Column(db.String(64), nullable=False)
    max_capacity = db.Column(db.Integer, nullable=False)
    
    students_tutorial = db.relationship('Student', foreign_keys='Student.tutorial_group_id', backref='tutorial_group', lazy=True)
    students_lab = db.relationship('Student', foreign_keys='Student.lab_group_id', backref='lab_group', lazy=True)
    teacher_groups = db.relationship('TeacherGroup', backref='group', lazy=True)
    change_group_requests_current = db.relationship('ChangeGroupRequest', foreign_keys='ChangeGroupRequest.current_group_id', backref='current_group', lazy=True)
    change_group_requests_requested = db.relationship('ChangeGroupRequest', foreign_keys='ChangeGroupRequest.requested_group_id', backref='requested_group', lazy=True)
    def to_dict(self):
        return {
            'group_id': self.group_id,
            'section_id': self.section_id,
            'section': self.section.to_dict() if self.section else None,
            'group_type': self.group_type,
            'group_name': self.group_name,
            'max_capacity': self.max_capacity,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Student(db.Model):
    __tablename__ = 'students'
    
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    matricule = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    nationality = db.Column(db.String(64), nullable=False)
    gender = db.Column(db.String(64), nullable=False)
    disability = db.Column(db.Boolean, nullable=False)
    phone_number = db.Column(db.String(64), nullable=False)
    observation = db.Column(db.String(255), nullable=False)
    speciality_id = db.Column(db.Integer, db.ForeignKey('specialities.speciality_id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.section_id'), nullable=False)
    tutorial_group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), nullable=False)
    lab_group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), nullable=False)
    
    requests = db.relationship('Request', backref='student', lazy=True)
    swap_group_requests_current = db.relationship('SwapGroupRequest', foreign_keys='SwapGroupRequest.current_student_id', backref='current_student', lazy=True)
    swap_group_requests_requested = db.relationship('SwapGroupRequest', foreign_keys='SwapGroupRequest.requested_student_id', backref='requested_student', lazy=True)
    swap_section_requests_current = db.relationship('SwapSectionRequest', foreign_keys='SwapSectionRequest.current_student_id', backref='current_student', lazy=True)
    swap_section_requests_requested = db.relationship('SwapSectionRequest', foreign_keys='SwapSectionRequest.requested_student_id', backref='requested_student', lazy=True)
    def to_dict(self):
        return {
            'student_id': self.student_id,
            'user_id': self.user_id,
            'user': self.user.to_dict() if self.user else None,
            'matricule': self.matricule,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'birth_date': self.birth_date.strftime('%d/%m/%Y') if self.birth_date else None,
            'nationality': self.nationality,
            'gender': self.gender,
            'disability': self.disability,
            'phone_number': self.phone_number,
            'observation': self.observation,
            'speciality_id': self.speciality_id,
            'speciality': self.speciality.to_dict() if self.speciality else None,
            'section_id': self.section_id,
            'section': self.section.to_dict() if self.section else None,
            'tutorial_group_id': self.tutorial_group_id,
            'tutorial_group': self.tutorial_group.to_dict() if self.tutorial_group else None,
            'lab_group_id': self.lab_group_id,
            'lab_group': self.lab_group.to_dict() if self.lab_group else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def validate_student(data, db):
        # check speciality exist
        speciality = db.session.execute(db.select(Speciality).filter_by(speciality_id=data["speciality_id"])).first()
        if not speciality:
            return jsonify({
                "error": "Invalid speciality",
            }), 400 
        
        # check if section exist and within the same speciality
        section = db.session.execute(db.select(Section).filter_by(section_id=data["section_id"], speciality_id=data["speciality_id"])).first()
        
        if not section:
            return jsonify({
                "error": "Invalid section",
            }), 400
            
        # check if valid group_td within the section
        group_td = db.session.execute(db.select(Group).filter_by(group_type="TD", group_id=data["tutorial_group_id"]), section_id=data["section_id"]).first()
        if not group_td:
            return jsonify({
                "error": "Invalid group TD"
            })
            
        # check if valid group_tp within the section
        group_tp = db.session.execute(db.select(Group).filter_by(group_type="TP", group_id=data["lab_group_id"]), section_id=data["section_id"]).first()
        if not group_td:
            return jsonify({
                "error": "Invalid group TP"
            })
        
        return None
        
class Staff(db.Model):
    __tablename__ = 'staffs'
    
    staff_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    grade = db.Column(db.String(128), nullable=False)
    
    def to_dict(self):
        return {
            'staff_id': self.staff_id,
            'user_id': self.user_id,
            'user': self.user.to_dict() if self.user else None,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'grade': self.grade,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class TeacherSection(db.Model):
    __tablename__ = 'teacher_sections'
    
    teacher_section_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.section_id'), nullable=False)
    
    def to_dict(self):
        return {
            'teacher_section_id': self.teacher_section_id,
            'teacher_id': self.teacher_id,
            'teacher': self.teacher.to_dict() if self.teacher else None,
            'section_id': self.section_id,
            'section': self.section.to_dict() if self.section else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class TeacherGroup(db.Model):
    __tablename__ = 'teacher_groups'
    
    teacher_groups_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), nullable=False)
    
    def to_dict(self):
        return {
            'teacher_groups_id': self.teacher_groups_id,
            'teacher_id': self.teacher_id,
            'teacher': self.teacher.to_dict() if self.teacher else None,
            'group_id': self.group_id,
            'group': self.group.to_dict() if self.group else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Request(db.Model):
    __tablename__ = 'requests'
    
    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    status = db.Column(db.String(64), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    
    change_group_requests = db.relationship('ChangeGroupRequest', backref='request', lazy=True)
    section_change_requests = db.relationship('SectionChangeRequest', backref='request', lazy=True)
    swap_group_requests = db.relationship('SwapGroupRequest', backref='request', lazy=True)
    swap_section_requests = db.relationship('SwapSectionRequest', backref='request', lazy=True)
    
    def to_dict(self):
        return {
            'request_id': self.request_id,
            'student_id': self.student_id,
            'student': self.student.to_dict() if self.student else None,
            'status': self.status,
            'reason': self.reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ChangeGroupRequest(db.Model):
    __tablename__ = 'change_group_requests'
    
    change_group_request_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.request_id'), nullable=False)
    current_group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), nullable=False)
    requested_group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), nullable=False)
    
    def to_dict(self):
        return {
            'change_group_request_id': self.change_group_request_id,
            'request_id': self.request_id,
            'request': self.request.to_dict() if self.request else None,
            'current_group_id': self.current_group_id,
            'current_group': self.current_group.to_dict() if self.current_group else None,
            'requested_group_id': self.requested_group_id,
            'requested_group': self.requested_group.to_dict() if self.requested_group else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SectionChangeRequest(db.Model):
    __tablename__ = 'section_change_requests'
    
    section_change_request_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.request_id'), nullable=False)
    current_section_id = db.Column(db.Integer, db.ForeignKey('sections.section_id'), nullable=False)
    requested_section_id = db.Column(db.Integer, db.ForeignKey('sections.section_id'), nullable=False)
    
    def to_dict(self):
        return {
            'section_change_request_id': self.section_change_request_id,
            'request_id': self.request_id,
            'request': self.request.to_dict() if self.request else None,
            'current_section_id': self.current_section_id,
            'current_section': self.current_section.to_dict() if self.current_section else None,
            'requested_section_id': self.requested_section_id,
            'requested_section': self.requested_section.to_dict() if self.requested_section else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    notification_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(128), nullable=False)
    is_read = db.Column(db.Boolean, nullable=False)
    
    def to_dict(self):
        return {
            'notification_id': self.notification_id,
            'user_id': self.user_id,
            'user': self.user.to_dict() if self.user else None,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SwapGroupRequest(db.Model):
    __tablename__ = 'swap_group_requests'
    
    swap_group_request_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.request_id'), nullable=False)
    current_student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    requested_student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    
    def to_dict(self):
        return {
            'swap_group_request_id': self.swap_group_request_id,
            'request_id': self.request_id,
            'request': self.request.to_dict() if self.request else None,
            'current_student_id': self.current_student_id,
            'current_student': self.current_student.to_dict() if self.current_student else None,
            'requested_student_id': self.requested_student_id,
            'requested_student': self.requested_student.to_dict() if self.requested_student else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SwapSectionRequest(db.Model):
    __tablename__ = 'swap_section_requests'
    
    swap_section_request_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.request_id'), nullable=False)
    current_student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    requested_student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    
    def to_dict(self):
        return {
            'swap_section_request_id': self.swap_section_request_id,
            'request_id': self.request_id,
            'request': self.request.to_dict() if self.request else None,
            'current_student_id': self.current_student_id,
            'current_student': self.current_student.to_dict() if self.current_student else None,
            'requested_student_id': self.requested_student_id,
            'requested_student': self.requested_student.to_dict() if self.requested_student else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }




# define routes
@app.route('/')
def add():
    return "test"



# =========================
# Roles ROUTES
# =========================
@app.route('/roles', methods=["GET"])
def get_roles():
    roles = Role.query.all()
    return jsonify([role.to_dict() for role in roles])

@app.route('/roles/<int:role_id>', methods=["GET"])
def get_role(role_id):
    role = Role.query.get(role_id)
    if role:
        return jsonify(role.to_dict())
    else:
        return jsonify({"error": "role not found"}), 404
    
@app.route('/roles', methods=["POST"])
def add_role():
    data = request.get_json()
    
    required_fields = ["role_name", "permission_level"]
    error = check_required_fields(required_fields, data)
    if error:
        return error
    
    error = run_validations([
        (check_unique_field, [Role, "role_name", data["role_name"], db]),
        (validate_positive_integer, [data["permission_level"], "permission_level"]),
    ])
    if error:
        return error
    
    
    # create new role
    new_role = Role(role_name=data["role_name"], permission_level=data["permission_level"])
    db.session.add(new_role)
    db.session.commit()
    
    return jsonify(new_role.to_dict()), 201

@app.route('/roles/<int:role_id>', methods=["PUT"])
def update_role(role_id):
    role = Role.query.get(role_id)
    if not role:
        return jsonify({
            "error": "Role not found"
        }), 404
    
    data = request.get_json()
    
    required_fields = ["role_name", "permission_level"]
    error = check_required_fields(required_fields, data)
    if error:
        return error
    
    error = run_validations([
        (check_unique_field, [Role, "role_name", data["role_name"], db, "role_id", role.role_id]),
        (validate_positive_integer, [data["permission_level"], "permission_level"])
    ])
    if error:
        return error
    
    # update
    role.role_name = data["role_name"]
    role.permission_level = data["permission_level"]
    db.session.commit()
    
    return jsonify({
        "message": "Updated succesfully"
    }), 200
    
@app.route('/roles/<int:role_id>', methods=["DELETE"])
def delete_role(role_id):
    role = Role.query.get(role_id)

    if not role:
        return jsonify({"error": "Role not found"}), 404

    if role.protected:
        return jsonify({"error": "This role cannot be deleted"}), 403

    db.session.delete(role)
    db.session.commit()
    return jsonify({"message": "Role deleted successfully"}), 200
       


# =========================
# Speciality ROUTES
# =========================
@app.route('/specialities', methods = ["GET"])
def get_specialities():
    specialities = Speciality.query.all()
    return jsonify([speciality.to_dict() for speciality in specialities])

@app.route('/specialities/<int:speciality_id>', methods = ["GET"])
def get_speciality(speciality_id):

    speciality = Speciality.query.get(speciality_id)

    if not speciality:
        return jsonify({
            "error" , "speciality not found"
            }) , 404
    
    return jsonify(speciality.to_dict()), 200

@app.route('/specialities/<int:speciality_id>', methods=["DELETE"])
def delete_speciality(speciality_id):
    speciality = Speciality.query.get(speciality_id)

    if not speciality:
        return jsonify({"error": "speciality not found"}),404
    db.session.delete(speciality)
    db.session.commit()
    return jsonify({"message": "speciality deleted sucessfully"}), 200

@app.route('/specialities', methods = ["POST"])
def add_speciality():
    data = request.get_json()
    
    # validation
    required_fields = ["name", "education_level"]
    error = check_required_fields(required_fields, data)
    if error:
        return error
    
    error = run_validations([
        (check_unique_field, [Speciality, "name", data["name"], db]),
        (validate_positive_integer, [data["name"], "name"])
    ])
    if error:
        return error
    
    
    # create new speciality
    new_speciality = Speciality(
        name = data["name"],
        education_level = data["education_level"]
    )

    db.session.add(new_speciality)
    db.session.commit()

    return jsonify(new_speciality.to_dict()), 201

@app.route('/specialities/<int:speciality_id>', methods=["PUT"])
def update_speciality(speciality_id):
    speciality = Speciality.query.get(speciality_id)
    
    if not speciality:
        return jsonify({
            "error" : "speciality not found"
            }), 404
        
    data = request.get_json()
    # validation
    required_fields = ["name", "education_level"]
    error = check_required_fields(required_fields, data)
    if error:
        return error
    
    error = run_validations([
        (check_unique_field, [Speciality, "name", data["name"], db, "speciality_id", speciality.speciality_id]),
        (validate_positive_integer, [data["education_level"], "education_level"])
    ])
    if error:
        return error
    
    # update
    speciality.name = data["name"]
    speciality.education_level = data["education_level"]
    db.session.commit()

    return jsonify({
        "message": "Updated succesfully"
    }), 200


# =========================
# Section ROUTES
# =========================














# =========================
# Users ROUTES
# =========================
@app.route('/users', methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/users/<int:user_id>', methods=["GET"])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify(user.to_dict()), 200
    else:
        return jsonify({"error": "User not found"}), 404



# =========================
# Students ROUTES
# =========================
@app.route('/students', methods=["GET"])
def get_students():
    students = Student.query.all()
    return jsonify([student.to_dict() for student in students])

@app.route('/students/<int:student_id>', methods=["GET"])
def get_student(student_id):
    student = Student.query.get(student_id)
    if student:
        return jsonify(student.to_dict())
    else:
        return jsonify({"error": "Student not found"}), 404

@app.route('/students', methods=["POST"])
def add_student():
    """
        REQUEST FORM:
        {
            "email": "example@gmail.com",
            "password": "12345678"
            "matricule": 02323245326,
            "first_name": "123456",
            "last_name": 1,
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
    error = check_required_fields(required_fields, data)
    if error:
        return error

    # give the student the role "Student" by default
    role = db.session.execute(db.select(Role).filter_by(role_name="Student")).first()
    data["role_id"] = role.role_id
    
    error = run_validations([
        (validate_email_format, [data["email"]]),
        (check_unique_field, [User, "email", data["email"], db]), # check for unique email in Users table
        (validate_password_length, [data["password"]]),
    ])
    if error:
        return error
    
    
    validation_error = Student.validate_student(data, db)
    if validation_error:
        return validation_error
    
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
    
    
    
    
    


    























# base roles
def insert_base_roles():
    base_roles = [
        {"role_name": "Student", "permission_level": 1, "protected": True},
        {"role_name": "Teacher", "permission_level": 2, "protected": True},
        {"role_name": "Admin", "permission_level": 5, "protected": True},
    ]

    for role_data in base_roles:
        exists = Role.query.filter_by(role_name=role_data['role_name']).first()
        if not exists:
            role = Role(**role_data)
            db.session.add(role)

    db.session.commit()
    print("Base roles inserted.")

# don't touch this
with app.app_context():
    insert_base_roles()
    db.create_all()
if __name__ == '__main__':
    app.run(debug=True)