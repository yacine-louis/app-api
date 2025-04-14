from flask import Blueprint, jsonify, request
from models.user import User
from models import db
from resources.validations import *

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/', methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/<int:user_id>', methods=["GET"])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify(user.to_dict()), 200
    else:
        return jsonify({"error": "User not found"}), 404