from flask import Flask, jsonify 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

from sqlalchemy import Column, Integer, String, MetaData, Table, TIMESTAMP, ForeignKey, Date, Text, Boolean

from sqlalchemy import select
from sqlalchemy.orm import relationship, Session, DeclarativeBase

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
    
    users = db.relationship('User', backref='role', lazy=True)

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)
    
    teachers = db.relationship('Teacher', backref='user', lazy=True)
    students = db.relationship('Student', backref='user', lazy=True)
    staffs = db.relationship('Staff', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)

class Specialty(db.Model):
    __tablename__ = 'specialties'
    
    speciality_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    education_level = db.Column(db.Integer, nullable=False)
    
    sections = db.relationship('Section', backref='specialty', lazy=True)
    students = db.relationship('Student', backref='specialty', lazy=True)

class Section(db.Model):
    __tablename__ = 'sections'
    
    section_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    speciality_id = db.Column(db.Integer, db.ForeignKey('specialties.speciality_id'), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    max_capacity = db.Column(db.Integer, nullable=False)
    
    groups = db.relationship('Group', backref='section', lazy=True)
    students = db.relationship('Student', backref='section', lazy=True)
    teacher_sections = db.relationship('TeacherSection', backref='section', lazy=True)

class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    teacher_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    grade = db.Column(db.String(128), nullable=False)
    
    teacher_sections = db.relationship('TeacherSection', backref='teacher', lazy=True)
    teacher_groups = db.relationship('TeacherGroup', backref='teacher', lazy=True)

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
    specialty_id = db.Column(db.Integer, db.ForeignKey('specialties.speciality_id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.section_id'), nullable=False)
    tutorial_group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), nullable=False)
    lab_group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), nullable=False)
    
    requests = db.relationship('Request', backref='student', lazy=True)
    swap_group_requests_current = db.relationship('SwapGroupRequest', foreign_keys='SwapGroupRequest.current_student_id', backref='current_student', lazy=True)
    swap_group_requests_requested = db.relationship('SwapGroupRequest', foreign_keys='SwapGroupRequest.requested_student_id', backref='requested_student', lazy=True)
    swap_section_requests_current = db.relationship('SwapSectionRequest', foreign_keys='SwapSectionRequest.current_student_id', backref='current_student', lazy=True)
    swap_section_requests_requested = db.relationship('SwapSectionRequest', foreign_keys='SwapSectionRequest.requested_student_id', backref='requested_student', lazy=True)

class Staff(db.Model):
    __tablename__ = 'staffs'
    
    staff_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    grade = db.Column(db.String(128), nullable=False)

class TeacherSection(db.Model):
    __tablename__ = 'teacher_sections'
    
    teacher_section_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.section_id'), nullable=False)

class TeacherGroup(db.Model):
    __tablename__ = 'teacher_groups'
    
    teacher_groups_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), nullable=False)

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

class ChangeGroupRequest(db.Model):
    __tablename__ = 'change_group_requests'
    
    change_group_request_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.request_id'), nullable=False)
    current_group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), nullable=False)
    requested_group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), nullable=False)

class SectionChangeRequest(db.Model):
    __tablename__ = 'section_change_requests'
    
    section_change_request_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.request_id'), nullable=False)
    current_section_id = db.Column(db.Integer, db.ForeignKey('sections.section_id'), nullable=False)
    requested_section_id = db.Column(db.Integer, db.ForeignKey('sections.section_id'), nullable=False)

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    notification_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(128), nullable=False)
    is_read = db.Column(db.Boolean, nullable=False)

class SwapGroupRequest(db.Model):
    __tablename__ = 'swap_group_requests'
    
    swap_group_request_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.request_id'), nullable=False)
    current_student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    requested_student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)

class SwapSectionRequest(db.Model):
    __tablename__ = 'swap_section_requests'
    
    swap_section_request_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.request_id'), nullable=False)
    current_student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    requested_student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)








# define routes
@app.route('/')
def add():
    return "test"



# =========================
# Roles ROUTES
# ========================
    


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
    """
        REQUEST FORM:
        {
            "role_name": "Staff",
            "permission_level": 3,
        }
        
        RETURN FORM:
        {
            'role_id': self.role_id,
            'role_name': "Staff",
            'permission_level': 3,
        }
    """
    data = request.get_json()
    
    new_role = Role(role_name=data["role_name"], permission_level=data["permission_level"])
    db.session.add(new_role)
    db.session.commit()
    
    return jsonify(new_role.to_dict()), 201

@app.route('/roles/<int:role_id>', methods=["PUT"])
def update_role(role_id):
    """
        REQUEST FORM:
        {
            "role_name": "Staff",
            "permission_level": 3,
        }
        
        RETURN FORM:
        {
            'role_id': self.role_id,
            'role_name': "Staff",
            'permission_level': 3,
        }
        
        ERROR:
        {
            "error": "role not found"
        }
    """
    data = request.get_json()
    role = Role.query.get(role_id)
    
    if role:
        role.role_name = data.get("role_name", role.role_name)
        role.permission_level = data.get("permission_level", role.permission_level)
        db.session.commit()
        return jsonify(role.to_dict())
    else:
        return jsonify({"error": "role not found"}), 404
    
@app.route('/roles/<int:role_id>', methods=["DELETE"])
def delete_role(role_id):
    role = Role.query.get(role_id)
    if role:
        db.session.delete(role)
        db.session.commit()
        return jsonify({"message": "role deleted succesfully"})
    else:
        return jsonify({"error": "role not found"}), 404
    
    
    


















# don't touch this
with app.app_context():
    db.create_all()
if __name__ == '__main__':
    app.run()