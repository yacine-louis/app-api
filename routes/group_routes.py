from flask import Blueprint, jsonify, request
from models import db, TeacherGroup, Group, Section
from resources.validations import *

group_bp = Blueprint('group_bp', __name__)


@group_bp.route('/<int:group_id>', methods=["GET"])
def get_group(group_id):
    group = Group.query.get(group_id)
    
    if not group:
        return jsonify({"error": "Group not found"}), 404
    
    teacher_id = db.session.query(TeacherGroup.teacher_id).filter(TeacherGroup.group_id == group_id).first()

    return jsonify({
            "success": True,
            "data": group.to_dict(),
            "teacher_id": teacher_id
        })
        
@group_bp.route('/<int:group_id>', methods=["PUT"])
def update_group(group_id):
    """
    {
        "group_name": 
        "max_capacity":
    }
    """
    group = Group.query.get(group_id)
    
    if not group:
        return jsonify({"error": "Group not found"}), 404

    data = request.get_json()
    
    error = run_validations([
        (validate_required_fields, [["group_name", "max_capacity"], data]),
        (validate_positive_integer, [data["max_capacity"], "max_capacity"]),
        (validate_unique_field, [Group, "group_name", data["group_name"], db, "group_id", group_id])
    ])
    if error:
        return jsonify(error), 400

    # update group
    group.group_name = data["group_name"]
    group.max_capacity = data["max_capacity"]
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Group updated successfully",
        "group": group.to_dict()
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
        }), 409

    db.session.delete(group)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Group deleted successfully"
        }), 200

@group_bp.route('/', methods=["GET"])
def get_groups():
    # Filters
    search_data = request.args.get("search_data", type=str)
    page = request.args.get("page", default=1, type=int)
    page_size = request.args.get("page_size", default=10, type=int)
    teacher_id = request.args.get("teacher_id", type=int)
    section_id = request.args.get("section_id", type=int)
    specialization_id = request.args.get("specialization_id", type=int)
    group_type = request.args.get("type", type=str)
    capacity = request.args.get("capacity", type=int)

    groups = Group.query

    if search_data:
        groups = groups.filter(Group.name.ilike(f"%{search_data}%"))
    if teacher_id:
        groups = groups.filter(Group.teacher_id == teacher_id)
    if section_id:
        groups = groups.filter(Group.section_id == section_id)
    if specialization_id:
        groups = groups.join(Section, Group.section_id == Section.section_id).filter(Section.speciality_id == specialization_id)
    if group_type:
        groups = groups.filter(Group.group_type == group_type)
    if capacity is not None:
        groups = groups.filter(Group.capacity <= capacity)
        
    groups = groups.paginate(page=page, per_page=page_size)

    return jsonify({
        "success": True,
        "data": [group.to_dict() for group in groups.items], 
        "pagination": {
            "totalItems": groups.total,
            "currentPage": groups.page,
            "pageSize": groups.per_page,
            "totalPages": groups.pages,
        }
    })

@group_bp.route('/', methods=["POST"])
def add_group():
    """
    REQUEST FORM:
    {
        "section_id": 1,
        "group_type": "lab",
        "group_name": "Group A",
        "max_capacity": 30
    }
    """
    data = request.get_json()
    
    error = run_validations([
        (validate_required_fields, [["section_id", "group_type", "group_name", "max_capacity"], data]),
        (validate_positive_integer, [data["max_capacity"], "max_capacity"]),
        (validate_unique_field, [Group, "group_name", data["group_name"], db]),
    ])
    if error:
        return jsonify(error), 400

    # Validate group_type is either lab or tutorial
    if data["group_type"] not in ["lab", "tutorial"]:
        return jsonify({"error": "Group type must be either lab or tutorial"}), 400

    # Check if section exists
    section = Section.query.get(data["section_id"])
    if not section:
        return jsonify({"error": "Section not found"}), 404

    # add new group
    new_group = Group(
        section_id=data["section_id"],
        group_type=data["group_type"],
        group_name=data["group_name"],
        max_capacity=data["max_capacity"]
    )

    db.session.add(new_group)
    db.session.commit()

    return jsonify({
            "success": True,
            "message": "Group created successfully",
            "group": new_group.to_dict()
        }), 201

@group_bp.route('/groups/change/<int:group_id>', methods=["PUT"])
def update_group_admin(group_id):
    """
    {
        "group_name": 
        "max_capacity":
    }
    """
    group = Group.query.get(group_id)
    
    if not group:
        return jsonify({"error": "Group not found"}), 404

    data = request.get_json()
    
    error = run_validations([
        (validate_required_fields, [["group_name", "max_capacity"], data]),
        (validate_positive_integer, [data["max_capacity"], "max_capacity"]),
        (validate_unique_field, [Group, "group_name", data["group_name"], db, "group_id", group_id])
    ])
    if error:
        return jsonify(error), 400

    # update group
    group.group_name = data["group_name"]
    group.max_capacity = data["max_capacity"]
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Group updated successfully",
        "group": group.to_dict()
    }), 200
    
