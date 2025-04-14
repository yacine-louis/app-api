from flask import Blueprint, jsonify, request
from models.role import Role
from models import db
from resources.validations import *

role_bp = Blueprint('role_bp', __name__)

@role_bp.route('/', methods=["GET"])
def get_roles():
    roles = Role.query.all()
    return jsonify([role.to_dict() for role in roles])

@role_bp.route('/<int:role_id>', methods=["GET"])
def get_role(role_id):
    role = Role.query.get(role_id)
    if role:
        return jsonify(role.to_dict())
    else:
        return jsonify({"error": "role not found"}), 404