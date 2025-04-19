from flask import Blueprint, jsonify, request
from models.speciality import Speciality
from models import db
from resources.validations import *

speciality_bp = Blueprint('speciality_bp', __name__)



@speciality_bp.route('/', methods=["GET"])
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

@speciality_bp.route('/<int:speciality_id>', methods = ["GET"])
def get_speciality(speciality_id):

    speciality = Speciality.query.get(speciality_id)

    if not speciality:
        return jsonify({
            "error": "speciality not found"
            }) , 404
    
    return jsonify(speciality.to_dict()), 200

@speciality_bp.route('/', methods = ["POST"])
def add_speciality():
    data = request.get_json()
    
    # validation
    required_fields = ["name", "education_level"]
    error = validate_required_fields(required_fields, data)
    if error:
        return jsonify(error), 400
    
    error = run_validations([
        (validate_unique_field, [Speciality, "name", data["name"], db]),
        (validate_positive_integer, [data["name"], "name"])
    ])
    if error:
        return jsonify(error), 400
    
    
    # create new speciality
    new_speciality = Speciality(
        name = data["name"],
        education_level = data["education_level"]
    )

    db.session.add(new_speciality)
    db.session.commit()

    return jsonify(new_speciality.to_dict()), 201

@speciality_bp.route('/<int:speciality_id>', methods=["PUT"])
def update_speciality(speciality_id):
    speciality = Speciality.query.get(speciality_id)
    
    if not speciality:
        return jsonify({
            "error" : "speciality not found"
            }), 404
        
    data = request.get_json()
    # validation
    required_fields = ["name", "education_level"]
    error = validate_required_fields(required_fields, data)
    if error:
        return jsonify(error), 400
    
    error = run_validations([
        (validate_unique_field, [Speciality, "name", data["name"], db, "speciality_id", speciality.speciality_id]),
        (validate_positive_integer, [data["education_level"], "education_level"])
    ])
    if error:
        return jsonify(error), 400
    
    # update
    speciality.name = data["name"]
    speciality.education_level = data["education_level"]
    db.session.commit()

    return jsonify({
        "message": "Updated succesfully"
    }), 200

@speciality_bp.route('/<int:speciality_id>', methods=["DELETE"])
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
