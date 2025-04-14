from flask import Blueprint, jsonify, request
from models.section import Section
from models import db
from resources.validations import *

section_bp = Blueprint('section_bp', __name__)


@section_bp.route('/', methods=["GET"])
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

@section_bp.route('/', methods = ["POST"])
def add_section():
    data = request.get_json()
    
    required_fields = ["speciality_id", "name", "max_capacity"]
    error = validate_required_fields(required_fields, data)
    if error:
        return error
    
    error = run_validations([
        (validate_unique_field, [Section, "name", data["name"], db]),
        (validate_positive_integer, [data["max_capacity"], "max_capacity"]),
    ])
    if error:
        return jsonify(error), 400
    
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

@section_bp.route('/<int:section_id>', methods=["DELETE"])
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
        
@section_bp.route('/<int:section_id>', methods=["GET"])
def get_section(section_id):
    section = Section.query.get(section_id)

    if section:
        return jsonify(section.to_dict()), 200
    else:
        return jsonify({"error": "Section not found"}), 404

@section_bp.route('/<int:section_id>', methods=["PUT"])
def update_section(section_id):
    section = Section.query.get(section_id)
    
    if not section:
        return jsonify({"error": "Section not found"}), 404

    data = request.get_json()

    required_fields = ["speciality_id", "name", "max_capacity"]
    error = validate_required_fields(required_fields, data)
    if error:
        return jsonify(error), 400

    error = run_validations([
        (validate_unique_field, [Section, "name", data["name"], db, "section_id", section.section_id]),
        (validate_positive_integer, [data["max_capacity"], "max_capacity"]),
    ])
    if error:
        return jsonify(error), 400
    
    speciality = Speciality.query.get(data["speciality_id"])
    if not speciality:
        return jsonify({"error": "Speciality not found"}), 404
    
    section.speciality_id = data["speciality_id"]
    section.name = data["name"]
    section.max_capacity = data["max_capacity"]
    db.session.commit()

    return jsonify(section.to_dict()), 200
