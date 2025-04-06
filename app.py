from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table, TIMESTAMP, ForeignKey, Date, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

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

db = SQLAlchemy(app)

engine = create_engine(f'mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_SECHEMA_NAME}')

# migrate database
migrate = Migrate(app, db)


# Define Table Classes
Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class Role(BaseModel):
    __tablename__ = 'roles'
    
    role_id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(255), nullable=False)
    permission_level = Column(Integer, nullable=False)
    
    users = relationship("User", back_populates="role")
    
    def to_dict(self):
        return {
            'role_id': self.role_id,
            'role_name': self.role_name,
            'permission_level': self.permission_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class User(BaseModel):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.role_id'), nullable=False)
    
    role = relationship("Role", back_populates="users")
    student = relationship("Student", uselist=False, back_populates="user")
    teacher = relationship("Teacher", uselist=False, back_populates="user")
    staff = relationship("Staff", uselist=False, back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'email': self.email,
            'role_id': self.role_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Specialty(BaseModel):
    __tablename__ = 'specialties'
    
    speciality_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    education_level = Column(Integer, nullable=False)
    
    sections = relationship("Section", back_populates="specialty")
    students = relationship("Student", back_populates="specialty")
    
    def to_dict(self):
        return {
            'speciality_id': self.speciality_id,
            'name': self.name,
            'education_level': self.education_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Section(BaseModel):
    __tablename__ = 'sections'
    
    section_id = Column(Integer, primary_key=True, autoincrement=True)
    speciality_id = Column(Integer, ForeignKey('specialties.speciality_id'), nullable=False)
    name = Column(String(255), nullable=False)
    
    specialty = relationship("Specialty", back_populates="sections")
    groups = relationship("Group", back_populates="section")
    students = relationship("Student", back_populates="section")
    teacher_sections = relationship("TeacherSection", back_populates="section")
    section_change_requests = relationship("SectionChangeRequest", foreign_keys="[SectionChangeRequest.current_section_id]", back_populates="current_section")
    requested_section_changes = relationship("SectionChangeRequest", foreign_keys="[SectionChangeRequest.requested_section_id]", back_populates="requested_section")
    
    def to_dict(self):
        return {
            'section_id': self.section_id,
            'speciality_id': self.speciality_id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Group(BaseModel):
    __tablename__ = 'groups'
    
    group_id = Column(Integer, primary_key=True, autoincrement=True)
    section_id = Column(Integer, ForeignKey('sections.section_id'), nullable=False)
    group_type = Column(String(255), nullable=False)
    group_name = Column(String(255), nullable=False)
    
    section = relationship("Section", back_populates="groups")
    teacher_groups = relationship("TeacherGroup", back_populates="group")
    tutorial_students = relationship("Student", foreign_keys="[Student.tutorial_group_id]", back_populates="tutorial_group")
    lab_students = relationship("Student", foreign_keys="[Student.lab_group_id]", back_populates="lab_group")
    change_group_requests_current = relationship("ChangeGroupRequest", foreign_keys="[ChangeGroupRequest.current_group_id]", back_populates="current_group")
    change_group_requests_requested = relationship("ChangeGroupRequest", foreign_keys="[ChangeGroupRequest.requested_group_id]", back_populates="requested_group")
    
    def to_dict(self):
        return {
            'group_id': self.group_id,
            'section_id': self.section_id,
            'group_type': self.group_type,
            'group_name': self.group_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Staff(BaseModel):
    __tablename__ = 'staffs'
    
    staff_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    grade = Column(String(255), nullable=False)
    
    user = relationship("User", back_populates="staff")
    requests = relationship("Request", back_populates="staff")
    
    def to_dict(self):
        return {
            'staff_id': self.staff_id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'grade': self.grade,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Teacher(BaseModel):
    __tablename__ = 'teachers'
    
    teacher_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    grade = Column(String(255), nullable=False)
    
    user = relationship("User", back_populates="teacher")
    teacher_sections = relationship("TeacherSection", back_populates="teacher")
    teacher_groups = relationship("TeacherGroup", back_populates="teacher")
    
    def to_dict(self):
        return {
            'teacher_id': self.teacher_id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'grade': self.grade,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Student(BaseModel):
    __tablename__ = 'students'
    
    student_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    matricule = Column(String(255), nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    birth_date = Column(Date, nullable=False)
    nationality = Column(String(255), nullable=False)
    gender = Column(String(255), nullable=False)
    disability = Column(Boolean, nullable=False)
    phone_number = Column(String(255), nullable=False)
    observation = Column(String(255), nullable=False)
    specialty_id = Column(Integer, ForeignKey('specialties.speciality_id'), nullable=False)
    section_id = Column(Integer, ForeignKey('sections.section_id'), nullable=False)
    tutorial_group_id = Column(Integer, ForeignKey('groups.group_id'), nullable=False)
    lab_group_id = Column(Integer, ForeignKey('groups.group_id'), nullable=False)
    
    user = relationship("User", back_populates="student")
    specialty = relationship("Specialty", back_populates="students")
    section = relationship("Section", back_populates="students")
    tutorial_group = relationship("Group", foreign_keys=[tutorial_group_id], back_populates="tutorial_students")
    lab_group = relationship("Group", foreign_keys=[lab_group_id], back_populates="lab_students")
    requests = relationship("Request", back_populates="student")
    
    def to_dict(self):
        return {
            'student_id': self.student_id,
            'user_id': self.user_id,
            'matricule': self.matricule,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name} {self.last_name}",
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'nationality': self.nationality,
            'gender': self.gender,
            'disability': self.disability,
            'phone_number': self.phone_number,
            'observation': self.observation,
            'specialty_id': self.specialty_id,
            'section_id': self.section_id,
            'tutorial_group_id': self.tutorial_group_id,
            'lab_group_id': self.lab_group_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class TeacherSection(BaseModel):
    __tablename__ = 'teacher_sections'
    
    teacher_section_id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey('teachers.teacher_id'), nullable=False)
    section_id = Column(Integer, ForeignKey('sections.section_id'), nullable=False)
    
    teacher = relationship("Teacher", back_populates="teacher_sections")
    section = relationship("Section", back_populates="teacher_sections")
    
    def to_dict(self):
        return {
            'teacher_section_id': self.teacher_section_id,
            'teacher_id': self.teacher_id,
            'section_id': self.section_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class TeacherGroup(BaseModel):
    __tablename__ = 'teacher_groups'
    
    teacher_groups_id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey('teachers.teacher_id'), nullable=False)
    group_id = Column(Integer, ForeignKey('groups.group_id'), nullable=False)
    
    teacher = relationship("Teacher", back_populates="teacher_groups")
    group = relationship("Group", back_populates="teacher_groups")
    
    def to_dict(self):
        return {
            'teacher_groups_id': self.teacher_groups_id,
            'teacher_id': self.teacher_id,
            'group_id': self.group_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Request(BaseModel):
    __tablename__ = 'requests'
    
    request_id = Column(Integer, primary_key=True, autoincrement=True)
    staff_id = Column(Integer, ForeignKey('staffs.staff_id'), nullable=False)
    student_id = Column(Integer, ForeignKey('students.student_id'), nullable=False)
    status = Column(String(255), nullable=False)
    reason = Column(Text, nullable=False)
    
    staff = relationship("Staff", back_populates="requests")
    student = relationship("Student", back_populates="requests")
    change_group_request = relationship("ChangeGroupRequest", uselist=False, back_populates="request")
    section_change_request = relationship("SectionChangeRequest", uselist=False, back_populates="request")
    
    def to_dict(self):
        return {
            'request_id': self.request_id,
            'staff_id': self.staff_id,
            'student_id': self.student_id,
            'status': self.status,
            'reason': self.reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ChangeGroupRequest(BaseModel):
    __tablename__ = 'change_group_requests'
    
    change_group_request_id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(Integer, ForeignKey('requests.request_id'), nullable=False)
    current_group_id = Column(Integer, ForeignKey('groups.group_id'), nullable=False)
    requested_group_id = Column(Integer, ForeignKey('groups.group_id'), nullable=False)
    
    request = relationship("Request", back_populates="change_group_request")
    current_group = relationship("Group", foreign_keys=[current_group_id], back_populates="change_group_requests_current")
    requested_group = relationship("Group", foreign_keys=[requested_group_id], back_populates="change_group_requests_requested")
    
    def to_dict(self):
        return {
            'change_group_request_id': self.change_group_request_id,
            'request_id': self.request_id,
            'current_group_id': self.current_group_id,
            'requested_group_id': self.requested_group_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SectionChangeRequest(BaseModel):
    __tablename__ = 'section_change_requests'
    
    section_change_request_id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(Integer, ForeignKey('requests.request_id'), nullable=False)
    current_section_id = Column(Integer, ForeignKey('sections.section_id'), nullable=False)
    requested_section_id = Column(Integer, ForeignKey('sections.section_id'), nullable=False)
    
    request = relationship("Request", back_populates="section_change_request")
    current_section = relationship("Section", foreign_keys=[current_section_id], back_populates="section_change_requests")
    requested_section = relationship("Section", foreign_keys=[requested_section_id], back_populates="requested_section_changes")
    
    def to_dict(self):
        return {
            'section_change_request_id': self.section_change_request_id,
            'request_id': self.request_id,
            'current_section_id': self.current_section_id,
            'requested_section_id': self.requested_section_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Notification(BaseModel):
    __tablename__ = 'notifications'
    
    notification_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(255), nullable=False)
    is_read = Column(Boolean, nullable=False)
    
    user = relationship("User", back_populates="notifications")
    
    def to_dict(self):
        return {
            'notification_id': self.notification_id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
Base.metadata.create_all(engine)



# define routes
@app.route('/')
def add():
    return "test"

















# don't touch this
if __name__ == '__main__':
    app.run()