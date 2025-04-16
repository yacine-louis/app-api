from flask import Blueprint, jsonify, request
from models import db, Student, Teacher, Staff, Section, Group, Request, Role, ChangeSectionRequest, ChangeGroupRequest,  SwapGroupRequest, SwapSectionRequest, TeacherGroup, TeacherSection
from resources.auth import token_required

stats_bp = Blueprint('stats_bp', __name__)

@stats_bp.route('/dashboard', methods=["GET"])
@token_required
def get_stats():
    """
    Returns role-dependent statistics for the dashboard.
    """
    user = getattr(request, 'user')  # Get the authenticated user
    role_name = user.role.role_name  # Get the user's role name

    if role_name == "Staff":
        total_students = Student.query.count()
        total_teachers = Teacher.query.count()
        total_staff = Staff.query.count()
        total_sections = Section.query.count()
        group_changes = ChangeGroupRequest.query.count() + SwapGroupRequest.query.count()
        section_changes = ChangeSectionRequest.query.count() + SwapSectionRequest.query.count()
        appeals = Request.query.filter_by(status="appeal").count()

        return jsonify({
            "success": True,
            "stats": {
                "total_students": total_students,
                "total_teachers": total_teachers,
                "total_staff": total_staff,
                "total_sections": total_sections,
                "group_changes": group_changes,
                "section_changes": section_changes,
                "appeals": appeals
            }
        }), 200

    elif role_name == "Teacher":
        teacher_id = user.teacher.teacher_id 
        active_groups = Group.query.join(Group.teacher_groups, Group.group_id == TeacherGroup.group_id).filter_by(teacher_id=teacher_id).count()
        active_sections = Section.query.join(Section.teacher_sections, Section.section_id == TeacherSection.section_id).filter_by(teacher_id=teacher_id).count()
        
        section_students = (
            db.session.query(Student.student_id)
            .join(Group, Student.group_id == Group.group_id)
            .join(Section, Group.section_id == Section.section_id)
            .join(TeacherSection, Section.section_id == TeacherSection.section_id)
            .filter(TeacherSection.teacher_id == teacher_id)
        )
        group_students = (
            db.session.query(Student.student_id)
            .join(Group, Student.group_id == Group.group_id)
            .join(TeacherGroup, Group.group_id == TeacherGroup.group_id)
            .filter(TeacherGroup.teacher_id == teacher_id)
        )
        
        union_query = section_students.union(group_students).subquery()
        total_students = db.session.query(func.count(func.distinct(union_query.c.student_id))).scalar()
        
        new_students = Request.query.filter_by(status="new_student").join(Student).join(Section.teacher_sections).filter_by(teacher_id=teacher_id).count()

        return jsonify({
            "success": True,
            "stats": {
                "active_groups": active_groups,
                "total_students": total_students,
                "active_sections": active_sections,
                "new_students": new_students
            }
        }), 200

    else:
        # If the user is not Staff or Teacher, return an error
        return jsonify({"error": "Unauthorized access"}), 403

