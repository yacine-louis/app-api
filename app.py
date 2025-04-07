from flask import Flask, jsonify 
from flask_migrate import Migrate

from sqlalchemy import select
from sqlalchemy.orm import  Session
from models import db

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
    

# =========================
# User ROUTES
# =========================


















# don't touch this
with app.app_context():
    db.create_all()
if __name__ == '__main__':
    app.run()