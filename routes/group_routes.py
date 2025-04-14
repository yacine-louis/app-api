from flask import Blueprint, jsonify, request
from models.group import Group
from models import db
from resources.validations import *

group_bp = Blueprint('group_bp', __name__)


@group_bp.route('/', methods=["GET"])
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

@group_bp.route('/<int:group_id>', methods=["GET"])
def get_group(group_id):
    group = Group.query.get(group_id)
    if group:
        return jsonify(group.to_dict())
    else:
        return jsonify({"error": "Group not found"}), 404

@group_bp.route('/', methods=["POST"])
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
    error = validate_required_fields(required_fields, data)
    if error:
        return jsonify(error), 400

    # Validate group_type is either TD or TP
    if data["group_type"] not in ["TD", "TP"]:
        return jsonify({"error": "Group type must be either TD or TP"}), 400

    # Check if section exists
    section = Section.query.get(data["section_id"])
    if not section:
        return jsonify({"error": "Section not found"}), 404
    
    error = run_validations([
        (validate_positive_integer, [data["max_capacity"], "max_capacity"]),
        (validate_unique_field, [Group, "group_name", data["group_name"], db, "section_id", data["section_id"]]),
    ])
    if error:
        return jsonify(error), 400

    

    new_group = Group(
        section_id=data["section_id"],
        group_type=data["group_type"],
        group_name=data["group_name"],
        max_capacity=data["max_capacity"]
    )

    db.session.add(new_group)
    db.session.commit()

    return jsonify(new_group.to_dict()), 201

@group_bp.route('/<int:group_id>', methods=["PUT"])
def update_group(group_id):
    group = Group.query.get(group_id)
    
    if not group:
        return jsonify({"error": "Group not found"}), 404

    data = request.get_json()
    
    required_fields = ["group_name", "max_capacity"]
    error = validate_required_fields(required_fields, data)
    if error:
        return jsonify(error), 400

    error = run_validations([
        (validate_positive_integer, [data["max_capacity"], "max_capacity"]),
        (validate_unique_field, [Group, "group_name", data["group_name"], db, "section_id", data["section_id"]]),
    ])
    if error:
        return jsonify(error), 400

    group.group_name = data["group_name"]
    group.max_capacity = data["max_capacity"]
    db.session.commit()

    return jsonify({
        "message": "Group updated successfully",
    }), 200

@group_bp.route('/<int:group_id>', methods=["DELETE"])
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

@group_bp.route('/<int:group_id>/students', methods=["GET"])
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


