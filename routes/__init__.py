from flask import Blueprint
from .user_routes import user_bp
from .role_routes import role_bp
from .speciality_routes import speciality_bp
from .section_routes import section_bp
from .group_routes import group_bp
from .student_routes import student_bp
from .staff_routes import staff_bp
from .stats_routes import stats_bp
from .teacher_routes import teacher_bp
from .request_routes import request_bp

def register_blueprints(app):
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(role_bp, url_prefix='/roles')
    app.register_blueprint(speciality_bp, url_prefix='/specialities')
    app.register_blueprint(section_bp, url_prefix='/sections')
    app.register_blueprint(group_bp, url_prefix='/groups')
    app.register_blueprint(student_bp, url_prefix='/students')
    app.register_blueprint(staff_bp, url_prefix='/staffs')
    app.register_blueprint(stats_bp, url_prefix='/stats')
    app.register_blueprint(teacher_bp, url_prefix='/teachers')
    app.register_blueprint(request_bp,url_prefix='/requests')

