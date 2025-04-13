from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from sqlalchemy import Column, Integer, String, MetaData, Table, TIMESTAMP, ForeignKey, Date, Text, Boolean

from sqlalchemy import select
from sqlalchemy.orm import relationship, Session, DeclarativeBase

from resources.validation import hash_password, check_password, check_required_fields, check_unique_field, validate_positive_integer, validate_email_format, validate_password_length, check_valid_date, run_validations

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
        group_td = db.session.execute(db.select(Group).filter_by(group_type="TD", group_id=data["tutorial_group_id"], section_id=data["section_id"])).first()
        if not group_td:
            return jsonify({
                "error": "Invalid group TD"
            }), 400
            
        # check if valid group_tp within the section
        group_tp = db.session.execute(db.select(Group).filter_by(group_type="TP", group_id=data["lab_group_id"], section_id=data["section_id"])).first()
        if not group_tp:
            return jsonify({
                "error": "Invalid group TP"
            }), 400
        
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
def test():
    return jsonify({
        "message": "Hello World!"
    })



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
    
    if role.protected:
        return jsonify({
            "error": "Can't modify protected role"
        }), 403
    
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
    
    user = db.session.execute(db.select(User).filter_by(role_id=role_id)).first()
    if user:
        return jsonify({"error": "Cannot delete role with assigned users"}), 403
    
    db.session.delete(role)
    db.session.commit()
    return jsonify({"message": "Role deleted successfully"}), 200
       


# =========================
# Speciality ROUTES
# =========================
@app.route('/specialities', methods=["GET"])
def get_specialities():
    # Get query parameters
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    name_filter = request.args.get('name')
    level_filter = request.args.get('level', type=int)
    
    # Base query
    query = Speciality.query
    
    # Apply filters
    if name_filter:
        query = query.filter(Speciality.name.ilike(f'%{name_filter}%'))
    if level_filter:
        query = query.filter(Speciality.education_level == level_filter)
    
    # Pagination
    paginated_specialities = query.paginate(
        page=page,
        per_page=per_page,
    )
    
    # Prepare response
    specialities_data = [speciality.to_dict() for speciality in paginated_specialities.items]
    
    return jsonify({
        'data': specialities_data,
        'pagination': {
            'total': paginated_specialities.total,
            'pages': paginated_specialities.pages,
            'current_page': paginated_specialities.page,
            'per_page': paginated_specialities.per_page,
        }
    })

@app.route('/specialities/<int:speciality_id>', methods = ["GET"])
def get_speciality(speciality_id):

    speciality = Speciality.query.get(speciality_id)

    if not speciality:
        return jsonify({
            "error": "speciality not found"
            }) , 404
    
    return jsonify(speciality.to_dict()), 200

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

@app.route('/specialities/<int:speciality_id>', methods=["DELETE"])
def delete_speciality(speciality_id):
    speciality = Speciality.query.get(speciality_id)

    if not speciality:
        return jsonify({"error": "speciality not found"}),404
    
    section = db.session.execute(db.select(Section).filter_by(speciality_id=speciality_id)).first()
    if section:
        return jsonify({"error": "can't delete Speciality with associated sections"}),400
    
    db.session.delete(speciality)
    db.session.commit()
    return jsonify({"message": "speciality deleted sucessfully"}), 200



# =========================
# Section ROUTES
# =========================
@app.route('/sections', methods=["GET"])
def get_sections():
    # filters
    name = request.args.get("name")
    page = request.args.get("page", default = 1, type=int)
    page_size = request.args.get("page_size", default = 10, type = int)
    teacher_id = request.args.get("teacher_id", type = int)
    speciality_id = request.args.get("speciality_id", type = int)
    level = request.args.get("level")

    sections = Section.query

    if name:
        sections = sections.filter(Section.name.ilike(f"{name}"))
    if teacher_id:
        sections = sections.join(TeacherSection).filter(TeacherSection.teacher_id == teacher_id)
    if speciality_id:
        sections = sections.filter(Section.speciality_id == speciality_id)
    if level:
        sections = sections.join(Speciality).filter(Speciality.education_level == level)
    
    sections = sections.paginate(page=page, per_page=page_size)

    return jsonify({
        "count" : sections.total,
        "page" : sections.page,
        "total_pages" : sections.pages,
        "sections": [section.to_dict() for section in sections.items],
        
    })

@app.route('/sections', methods = ["POST"])
def add_section():
    data = request.get_json()
    
    required_fields = ["speciality_id", "name", "max_capacity"]
    error = check_required_fields(required_fields, data)
    if error:
        return error
    
    error = run_validations([
        (check_unique_field, [Section, "name", data["name"], db]),
        (validate_positive_integer, [data["max_capacity"], "max_capacity"]),
    ])
    if error:
        return error
    
    speciality = Speciality.query.get(data["speciality_id"])
    if not speciality:
        return jsonify({"error": "speciality not found"}), 404
    
    new_section = Section(
        speciality_id = data["speciality_id"],
        name = data["name"],
        max_capacity = data["max_capacity"]
    )

    db.session.add(new_section)
    db.session.commit()
    
    return jsonify(new_section.to_dict()), 201

@app.route('/sections/<int:section_id>', methods=["DELETE"])
def delete_section(section_id):
    section = Section.query.get(section_id)
    
    if not section:
        return jsonify({"error": "section not found"}), 404
    
    if section.students:
        return jsonify({
            "error": "Cannot delete section with assigned students"
        }), 400
        
    # Check if section has any groups
    if section.groups:
        return jsonify({
            "error": "Cannot delete section with assigned groups",
        }), 400
        
    # Check if section has any teacher associations
    if section.teacher_sections:
        return jsonify({
            "error": "Cannot delete section with assigned teachers",
        }), 400
        
        
    db.session.delete(section)
    db.session.commit()
    return jsonify({"message": "section deleted succesfully"}),200
        
@app.route('/sections/<int:section_id>', methods=["GET"])
def get_section(section_id):
    section = Section.query.get(section_id)

    if section:
        return jsonify(section.to_dict()), 200
    else:
        return jsonify({"error": "Section not found"}), 404

@app.route('/sections/<int:section_id>', methods=["PUT"])
def update_section(section_id):
    section = Section.query.get(section_id)
    
    if not section:
        return jsonify({"error": "Section not found"}), 404

    data = request.get_json()

    required_fields = ["speciality_id", "name", "max_capacity"]
    error = check_required_fields(required_fields, data)
    if error:
        return error

    error = run_validations([
        (check_unique_field, [Section, "name", data["name"], db, "section_id", section.section_id]),
        (validate_positive_integer, [data["max_capacity"], "max_capacity"]),
    ])
    if error:
        return error
    
    speciality = Speciality.query.get(data["speciality_id"])
    if not speciality:
        return jsonify({"error": "Speciality not found"}), 404
    
    section.speciality_id = data["speciality_id"]
    section.name = data["name"]
    section.max_capacity = data["max_capacity"]
    db.session.commit()

    return jsonify(section.to_dict()), 200


# =========================
# Groups ROUTES
# =========================
@app.route('/groups', methods=["GET"])
def get_groups():
    # Filters
    group_type = request.args.get("group_type")
    section_id = request.args.get("section_id", type=int)
    page = request.args.get("page", default=1, type=int)
    page_size = request.args.get("page_size", default=10, type=int)

    groups = Group.query

    if group_type:
        groups = groups.filter(Group.group_type == group_type)
    if section_id:
        groups = groups.filter(Group.section_id == section_id)

    groups = groups.paginate(page=page, per_page=page_size)

    return jsonify({
        "count": groups.total,
        "page": groups.page,
        "total_pages": groups.pages,
        "groups": [group.to_dict() for group in groups.items]
    })

@app.route('/groups/<int:group_id>', methods=["GET"])
def get_group(group_id):
    group = Group.query.get(group_id)
    if group:
        return jsonify(group.to_dict())
    else:
        return jsonify({"error": "Group not found"}), 404

@app.route('/groups', methods=["POST"])
def add_group():
    """
    REQUEST FORM:
    {
        "section_id": 1,
        "group_type": "TD" or "TP",
        "group_name": "Group A",
        "max_capacity": 30
    }
    """
    data = request.get_json()
    
    required_fields = ["section_id", "group_type", "group_name", "max_capacity"]
    error = check_required_fields(required_fields, data)
    if error:
        return error

    # Validate group_type is either TD or TP
    if data["group_type"] not in ["TD", "TP"]:
        return jsonify({"error": "Group type must be either TD or TP"}), 400

    # Check if section exists
    section = Section.query.get(data["section_id"])
    if not section:
        return jsonify({"error": "Section not found"}), 404
    
    error = run_validations([
        (validate_positive_integer, [data["max_capacity"], "max_capacity"]),
        (check_unique_field, [Group, "group_name", data["group_name"], db, "section_id", data["section_id"]]),
    ])
    if error:
        return error

    

    new_group = Group(
        section_id=data["section_id"],
        group_type=data["group_type"],
        group_name=data["group_name"],
        max_capacity=data["max_capacity"]
    )

    db.session.add(new_group)
    db.session.commit()

    return jsonify(new_group.to_dict()), 201

@app.route('/groups/<int:group_id>', methods=["PUT"])
def update_group(group_id):
    group = Group.query.get(group_id)
    
    if not group:
        return jsonify({"error": "Group not found"}), 404

    data = request.get_json()
    
    required_fields = ["group_name", "max_capacity"]
    error = check_required_fields(required_fields, data)
    if error:
        return error

    error = run_validations([
        (validate_positive_integer, [data["max_capacity"], "max_capacity"]),
        (check_unique_field, [Group, "group_name", data["group_name"], db, "section_id", data["section_id"]]),
    ])
    if error:
        return error

    group.group_name = data["group_name"]
    group.max_capacity = data["max_capacity"]
    db.session.commit()

    return jsonify({
        "message": "Group updated successfully",
    }), 200

@app.route('/groups/<int:group_id>', methods=["DELETE"])
def delete_group(group_id):
    group = Group.query.get(group_id)
    
    if not group:
        return jsonify({"error": "Group not found"}), 404

    # Check if group has students assigned
    if group.students_tutorial or group.students_lab:
        return jsonify({
            "error": "Cannot delete group with assigned students"
        }), 400

    db.session.delete(group)
    db.session.commit()

    return jsonify({"message": "Group deleted successfully"}), 200

@app.route('/groups/<int:group_id>/students', methods=["GET"])
def get_group_students(group_id):
    group = Group.query.get(group_id)
    
    if not group:
        return jsonify({"error": "Group not found"}), 404

    # Get students based on group type
    if group.group_type == "TD":
        students = group.students_tutorial
    else:
        students = group.students_lab

    return jsonify([student.to_dict() for student in students])



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
    
#get students by speciality and section:
@app.route('/students/speciality/<int:speciality_id>/section/<int:section_id>', methods = ["GET"])
def get_students_v2(speciality_id,section_id):
    students = db.session.query(Student).filter(
        Student.speciality_id == speciality_id,
        Student.section_id  == section_id
    ).all()
    if not students:
        return jsonify({"error" : "no students found for given speciality and section"}),404
    return jsonify([student.to_dict() for student in students]),200



@app.route('/students', methods=["POST"])
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
    error = check_required_fields(required_fields, data)
    if error:
        return error

    
    
    error = run_validations([
        (validate_email_format, [data["email"]]),
        (check_unique_field, [User, "email", data["email"], db]), # check for unique email in Users table
        (validate_password_length, [data["password"]]),
        (check_valid_date, data["birth_date"]),
    ])
    if error:
        return error
    
    
    validation_error = Student.validate_student(data, db)
    if validation_error:
        return validation_error
    
    
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
    
@app.route('/students/<int:student_id>', methods=["DELETE"])
def delete_student(student_id):
    student = Student.query.get(student_id)
    
    if not student:
        return jsonify({
            "error": "Student not found"
        }), 404
    
    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "student deleted sucessfully"}), 200
    
@app.route('/students/<int:student_id>', methods=["PUT"])
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
    error = check_required_fields(required_fields, data)
    if error:
        return error
    
    error = check_valid_date(data["birth_date"])
    if error:
        return error
    

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



# =========================
# Staff ROUTES
# =========================
@app.route('/staffs', methods=["GET"])
def get_staffs():
    staffs = Staff.query.all()
    return jsonify([staff.to_dict() for staff in staffs])

@app.route('/staffs/<int:staff_id>', methods=["GET"])
def get_staff(staff_id):
    staff = Staff.query.get(staff_id)
    
    if not staff:
        return jsonify({
            "error": "Staff not found"
        }), 404

    return jsonify(staff.to_dict())

@app.route('/staffs', methods=["POST"])
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
    error = check_required_fields(required_fields, data)
    if error:
        return error
    
    
    error = run_validations([
        (validate_email_format, [data["email"]]),
        (check_unique_field, [User, "email", data["email"], db]), # check for unique email in Users table
        (validate_password_length, [data["password"]]),
    ])
    if error:
        return error
    
    
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

@app.route('/staffs/<int:staff_id>', methods=["PUT"])
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
    error = check_required_fields(required_fields, data)
    if error:
        return error
    
    staff.first_name=data["first_name"]
    staff.last_name=data["last_name"]
    staff.grade=data["grade"]
    
    db.session.commit()
    
    return jsonify({
        "message": "Updated succesfully"
    }), 200

@app.route('/staffs/<int:staff_id>', methods=["DELETE"])
def delete_staff(staff_id):
    staff = Staff.query.get(staff_id)
    
    if not staff:
        return jsonify({
            "error": "Staff not found"
        }), 404
    
    db.session.delete(staff)
    db.session.commit()
    
    return jsonify({"message": "staff deleted sucessfully"}), 200
    
    
    
# =========================
# Teachers ROUTES
# =========================
@app.route('/teachers', methods=["GET"])
def get_teachers():
    teachers = Teacher.query.all()
    if not teachers:
        return jsonify({"error" : "no teacher found"}),404
    return [teacher.to_dict() for teacher in teachers],200

@app.route('/teachers/<int:teacher_id>',methods=["GET"])
def get_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({"error" : "no teacher found"}),404
    return jsonify(teacher.to_dict()),200

@app.route('/teachers', methods = ["POST"])
def add_teacher():
    data = request.get_json()
    required_fields = ["user_id","first_name","last_name","grade"]
    error = run_validations(check_required_fields(required_fields, data)
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
    

@app.route('/teachers/<int:teacher_id>', methods=["PUT"])
def update_teacher(teacher_id):
     
    teacher = Teacher.query.get(teacher_id)
     
    if not teacher:
        return jsonify({"error" : "teacher not found"}),400
    teacher_user_id = teacher.user_id
    data = request.get_json()
    required_fields = ["user_id","first_name","last_name","grade"]
    error = run_validations(check_required_fields(required_fields, data)
, validate_positive_integer(data["user_id"], "User id"), check_unique_field(Teacher,"user_id", data["user_id"], db,"user_id",teacher_user_id))
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

@app.route('/teachers/<int:teacher_id>', methods=["DELETE"])
def delete_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({"error : teacher not found"}),400
    db.session.delete(teacher)
    db.session.commit()
    return jsonify({"message":"teacher deleted sucessfully"}),200



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

import random
from datetime import datetime, timedelta

def generate_test_data(db):
    """Generate complete test data including roles, specialties, sections, groups, and students"""
    try:
        # Clear existing test data first (optional)
        db.session.query(Student).delete()
        db.session.query(Group).delete()
        db.session.query(Section).delete()
        db.session.query(Speciality).delete()
        db.session.query(User).delete()
        db.session.commit()

        # Sample data lists
        first_names = ["Alice", "Bob", "Charlie", "David", "Eve", 
                      "Frank", "Grace", "Henry", "Ivy", "Jack"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", 
                     "Miller", "Davis", "Garcia", "Wilson", "Taylor"]
        countries = ["USA", "Canada", "UK", "France", "Germany", 
                    "Japan", "Australia", "Brazil", "India", "China"]
        
        # 1. Create required roles if they don't exist
        roles = [
            {"role_name": "Student", "permission_level": 1, "protected": True},
            {"role_name": "Teacher", "permission_level": 2, "protected": True},
            {"role_name": "Admin", "permission_level": 3, "protected": True}
        ]
        
        for role_data in roles:
            if not db.session.execute(db.select(Role).filter_by(role_name=role_data["role_name"])).scalar_one_or_none():
                db.session.add(Role(**role_data))
        db.session.commit()

        # Get the student role ID
        student_role = db.session.execute(
            db.select(Role).filter_by(role_name="Student")
        ).scalar_one()

        # 2. Create Specialties
        specialties = [
            Speciality(name="Computer Science", education_level=3),
            Speciality(name="Electrical Engineering", education_level=3),
            Speciality(name="Mathematics", education_level=3),
        ]
        db.session.add_all(specialties)
        db.session.commit()

        # 3. Create Sections
        sections = []
        for specialty in specialties:
            for i in range(1, 3):  # 2 sections per specialty
                section = Section(
                    speciality_id=specialty.speciality_id,
                    name=f"{specialty.name[:3]}-{i}",
                    max_capacity=30
                )
                sections.append(section)
        db.session.add_all(sections)
        db.session.commit()

        # 4. Create Groups
        groups = []
        for section in sections:
            # TD Groups
            for i in range(1, 3):
                groups.append(Group(
                    section_id=section.section_id,
                    group_type="TD",
                    group_name=f"TD-{section.name}-{i}",
                    max_capacity=15
                ))
            # TP Groups
            for i in range(1, 4):
                groups.append(Group(
                    section_id=section.section_id,
                    group_type="TP",
                    group_name=f"TP-{section.name}-{i}",
                    max_capacity=10
                ))
        db.session.add_all(groups)
        db.session.commit()

        # 5. Create Students with unique emails
        used_emails = set()
        
        for i in range(1, 21):  # 20 students
            section = random.choice(sections)
            td_groups = [g for g in groups if g.section_id == section.section_id and g.group_type == "TD"]
            tp_groups = [g for g in groups if g.section_id == section.section_id and g.group_type == "TP"]

            # Generate unique email
            while True:
                email = f"student{i}@university.edu"
                if email not in used_emails:
                    used_emails.add(email)
                    break
                i += 1

            # Create user
            user = User(
                email=email,
                hashed_password="password123",
                role_id=student_role.role_id
            )
            db.session.add(user)
            db.session.flush()  # Get the user_id

            # Random birth date (18-25 years old)
            birth_date = datetime.now() - timedelta(days=random.randint(365*18, 365*25))

            # Create student
            student = Student(
                user_id=user.user_id,
                matricule=f"2023-{random.randint(1000, 9999)}",
                first_name=random.choice(first_names),
                last_name=random.choice(last_names),
                birth_date=birth_date,
                nationality=random.choice(countries),
                gender=random.choice(["Male", "Female"]),
                disability=random.choice([True, False]),
                phone_number=f"06{random.randint(10, 99)}{random.randint(10, 99)}{random.randint(10, 99)}{random.randint(10, 99)}",
                observation="Test student",
                speciality_id=section.speciality_id,
                section_id=section.section_id,
                tutorial_group_id=random.choice(td_groups).group_id,
                lab_group_id=random.choice(tp_groups).group_id
            )
            db.session.add(student)
        
        db.session.commit()
        return {
            "status": "success",
            "counts": {
                "roles": 3,
                "specialties": len(specialties),
                "sections": len(sections),
                "groups": len(groups),
                "students": 20
            }
        }

    except Exception as e:
        db.session.rollback()
        return {
            "status": "error",
            "message": str(e)
        }


# don't touch this
with app.app_context():
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    if 'roles' in inspector.get_table_names():
         insert_base_roles()
    generate_test_data(db)
    db.create_all()
if __name__ == '__main__':
    app.run(debug=True)