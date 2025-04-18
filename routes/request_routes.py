from flask import Blueprint, jsonify, request
from models import db
from models.student import Student
from models.request import Request,RequestStatus,RequestType,RequestUrgency,filter_by_request_type,get_request_type
from models.change_group_request import ChangeGroupRequest
from models.change_section_request import ChangeSectionRequest
from models.swap_group_request import SwapGroupRequest
from models.swap_section_request import SwapSectionRequest
from models.notification import Notification, NotificationType
from models.teacher_section import TeacherSection
from models.teacher import Teacher
from models.teacher_group import TeacherGroup
from models.user import User
from models.section import Section
from models.group import Group
from sqlalchemy import exists
from resources.validations import *

request_bp = Blueprint('request_bp',__name__)

@request_bp.route('/',methods = ["GET"])
def get_requests():
    requests = db.session.query(Request).join(Student).join(ChangeGroupRequest, ChangeGroupRequest.request_id == Request.request_id, isouter=True) \
     .join(ChangeSectionRequest, ChangeSectionRequest.request_id == Request.request_id, isouter=True) \
     .join(SwapGroupRequest, SwapGroupRequest.request_id == Request.request_id, isouter=True) \
     .join(SwapSectionRequest, SwapSectionRequest.request_id == Request.request_id, isouter=True)

    search_data = request.args.get("search_data")
    student_id = request.args.get("student_id")
    status = request.args.get("status")
    request_type = request.args.get("type")
    urgency = request.args.get("urgency")
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    page = request.args.get("page", default = 1, type=int)
    page_size = request.args.get("page_size", default = 10, type = int)

    if search_data:
        if search_data.isdigit():
            student_id = int(search_data)
            requests = requests.filter(Request.student_id == student_id)
        else:
            student_name = search_data.strip()
            requests = requests.filter(Student.last_name == student_name)
    if student_id:
        try:
            student_id = int(student_id)
    
        except ValueError:
            return jsonify({"error":"Student ID must be a valid integer" }),400
        
        error = validate_positive_integer(student_id,"Student ID")
        if error:
            return jsonify(error),400
        
        requests = requests.filter(Request.student_id == student_id)

    if status:
        try:
            status = RequestStatus(status.lower())
        except ValueError:
            return jsonify({f"error" : "invalid status : {status}"}),400
        requests = requests.filter(Request.status == status)
    if request_type:
        try:
            request_type =  RequestType(request_type.lower())
        except ValueError:
            return jsonify({f"error" : "invalid type : {request_type}"}),400
        requests = filter_by_request_type(requests,request_type)
    
    if urgency:
        try:
            urgency=int(urgency)
            RequestUrgency(urgency)
            error = validate_positive_integer(urgency,"Urgency")
            if error:
                return jsonify(error),400
        except ValueError:
            return jsonify({"error": "invalid urgency level"}),400
        requests = requests.filter(Request.urgency == urgency)
    
   
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        requests = requests.filter(Request.created_at >= start_date)

    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        end_date = end_date.replace(hour=23, minute=59, second=59) #this we do it to make sure the end date until the last sec of the day.
        requests = requests.filter(Request.created_at <= end_date)
    
    requests = requests.order_by(Request.created_at.desc())#here we order the requests in descending order based on created_at
    requests = requests.paginate(page=page, per_page=page_size)

    response_data = []
    for row in requests.items:
        student_name = f"{row.first_name} {row.last_name}"
        request_type = get_request_type(row)

        response_data.append({
        "request_id": row.request_id,
        "date": row.created_at.strftime("%Y-%m-%d %H:%M"),
        "student_name": student_name,
        "student_id": row.student_id,
        "status": row.status,
        "urgency": row.urgency,
        "type": request_type
        })

    return jsonify({
    "success": True,
    "data" : response_data,
    "pagination" : {
    "totalItems": requests.total,
    "currentPage": requests.page,
    "pageSize": requests.per_page,
    "totalPages": requests.pages
    }}),200

@request_bp.route('/<int:request_id>', methods=["GET"])
def get_request(request_id):
    request_type = request.args.get("type")

    if not request_type:
        return jsonify({"error": "Invalid type"}), 400
    try:
        RequestType(request_type.lower())
    except ValueError:
        return jsonify({"error" :"Invalid type"}),400

        
    base_request = db.session.query(Request).filter(Request.request_id == request_id).first()
    if not base_request:
        return jsonify({"error": "request id not found"}), 404

    student = Student.query.filter(Student.student_id == base_request.student_id).first()

    detail_data = {}
    if request_type == RequestType.group:
        detail_data = db.session.query(ChangeGroupRequest).filter_by(request_id=request_id).first() \
            or db.session.query(SwapGroupRequest).filter_by(request_id=request_id).first()
    else:
        detail_data = db.session.query(ChangeSectionRequest).filter_by(request_id=request_id).first() \
            or db.session.query(SwapSectionRequest).filter_by(request_id=request_id).first()

    if not detail_data:
        return jsonify({"error": f"No {request_type} request details found for request_id {request_id}"}), 404

    response = {
        "request_id": base_request.request_id,
        "status": base_request.status,
        "urgency": base_request.urgency,
        "reason": base_request.reason,
        "created_at": base_request.created_at.strftime("%Y-%m-%d %H:%M"),
        "student": {
            "id": student.student_id,
            "name": f"{student.first_name} {student.last_name}",
            "nationality": student.nationality,
            "gender": student.gender,
            "phone_number": student.phone_number,
            "speciality_id": student.speciality_id,
            "section_id": student.section_id,
            "tutorial_group_id": student.tutorial_group_id,
            "lab_group_id": student.lab_group_id
        },
        "details": detail_data.to_dict()
    }

    return jsonify(response), 200

@request_bp.route('/change' , methods = ["POST"])
def change_request():
    data = request.get_json()
    required_fields = ["student_id", "current_id","requested_id","reason","urgency","type"]
    error = run_validations(validate_required_fields(required_fields,data), validate_positive_integer(data["student_id"],"student_id"), validate_positive_integer(data["current_id"],"current_id"),
                            validate_positive_integer(data["requested_id"],"requested_id"))
    if error:
        return jsonify(error),400
    student_id = data["student_id"]
    current_id = data["current_id"]
    requested_id = data["requested_id"]
    reason = data["reason"]
    urgency = data["urgency"]
    request_type = data["type"]

    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error":"student id not found"}),400
    try:
        RequestUrgency(urgency)
    except ValueError:
        return jsonify({"error":"invalid urgency level"}),400
    request_type = request_type.lower()
    try:
        RequestType(request_type)
    except ValueError:
        return jsonify({"error" : "invalid request type"}),400
    
    if request_type == RequestType.section:
        current_section = Section.query.get(current_id)
        if not current_section:
            return jsonify({"error": "invalid current section id"}),400
        requested_section = Section.query.get(requested_id)
        if not requested_section:
            return jsonify({"error": "invalid requested section id"}),400
        new_request = Request(
            student_id = student_id,
            status = RequestStatus.pending,
            reason = reason,
            urgency = urgency
        )
        db.session.add(new_request)
        db.session.flush()#since we need the request_id we do flush and not commit the changes yet to the database
        new_change_section_request =  ChangeSectionRequest(   
        request_id = new_request.request_id,
        current_section_id = current_id,
        requested_section_id = requested_id
    
       )
        db.session.add(new_change_section_request)
        db.session.commit()
        return jsonify({"message": "change section request submited suecessfuly"}),200
    elif request_type == RequestType.group:
        current_group = Group.query.get(current_id)
        if not current_group:
            return jsonify({"error":"current group id not found"}),400
        requested_group = Group.query.get(requested_id)
        if not requested_group:
            return jsonify({"error":"requsted group id not found"}),400
        new_request = Request(
            student_id = student_id,
            status = RequestStatus.pending,
            reason = reason,
            urgency = urgency
        )
        db.session.add(new_request)
        db.session.flush()
        new_change_group_request = ChangeGroupRequest(
            request_id = new_request.request_id,
            current_group_id = current_id,
            requested_group_id = requested_id

        )
        db.session.add(new_change_group_request)
        db.session.commit()
        return jsonify({"message":"group change request submited sucessfuly"}),200
@request_bp.route('/change/status' , methods = ["PATCH"])
def review_request():
    data = request.get_json()
    required_fields = ["request_id", "status", "type", "comment"]
    error = run_validations(validate_required_fields(required_fields,data), validate_positive_integer(data["request_id"],"request_id"))
    if error:
        return jsonify(error)
    request_id = data["request_id"]
    status = data["status"]
    request_type = data ["type"]
    comment = data["comment"]
    current_request = Request.query.get(request_id)
    if not current_request:
        return jsonify({"error":"request id not found"}),400
    request_type = request_type.lower()
    try:
        RequestType(request_type)
    except ValueError:
        return jsonify({f"error":"invalid request type {request_type}"})
    status = status.lower()
    try:
        RequestStatus(status)
    except ValueError:
        return jsonify({f"error":"invalid status {status}"}),400
    if status == RequestStatus.approved:
        if request_type == RequestType.section:
            current_change_section_request = db.session.query(ChangeSectionRequest).join(Request, ChangeSectionRequest.request_id == Request.request_id).filter(ChangeSectionRequest.request_id == current_request.request_id).first()
            if not current_change_section_request:
                return jsonify({"error" : "cannot find the change section request corresponded to the request id"}),404
            student = Student.query.get(current_request.student_id)
            if not student:
                return jsonify({"error": "cannot find the student corresponded to the given request"}),404
            requested_section = Section.query.get(current_change_section_request.requested_section_id)
            if not requested_section:
                return jsonify({"error" : "cannot find the corrseponded section to the change section request"}),404
            student.section_id = current_change_section_request.requested_section_id
            current_request.status = RequestStatus.approved

            #now we create a notification for the student and for the teachers holding the section
            user_exists = db.session.query(exists().where(User.user_id == student.user_id)).scalar()
            if not user_exists:
                return jsonify({"error":"cannot find the user id of the current student"}),404
            
            student_notification = Notification(
             user_id = student.user_id,
             title = "Change Section Request Response",
             message = f"request approved, you have been moved to section {requested_section.name}. ",
             notification_type = NotificationType.sucess,
             is_read = False
            )
            db.session.add(student_notification)
            teachers = db.session.query(Teacher).join(TeacherSection, Teacher.teacher_id == TeacherSection.teacher_id).filter(TeacherSection.section_id == student.section_id).all()
            for teacher in teachers:
                teacher_notification = Notification(
                user_id=teacher.user_id,
                title="Student Change Section Request",
                message=f"Student {student.name} was added to section {requested_section.name}.",
                notification_type=NotificationType.info,
                is_read=False)
                db.session.add(teacher_notification)

            db.session.commit()
        elif request_type == RequestType.group:
            current_change_group_request = db.session.query(ChangeGroupRequest).join(Request, ChangeGroupRequest.request_id == Request.request_id).filter(ChangeGroupRequest.request_id == current_request.request_id).first()
            if not current_change_group_request:
                return jsonify({"error" : "cannot find the change group request corresponded to the request id"}),404
            student = Student.query.get(current_request.student_id)
            if not student:
                return jsonify({"error": "cannot find the student corresponded to the given request"}),404
            requested_group = db.session.query.get(current_change_group_request.requested_group_id)
            if not requested_group:
                return jsonify({"error" : "cannot find the corrseponded group to the change section request"}),404
            #needs review (i dont know if we should seperate lab and tutorial or consider both as one??):
            #--
            student.tutorial_group_id = current_change_group_request.requested_group_id
            student.lab_group_id = current_change_group_request.requested_group_id
            #--
            current_request.status = RequestStatus.approved
            student_notification = Notification(
             user_id = student.user_id,
             title = "Change Group Request Response",
             message = f"request approved, you have been moved to Group {requested_group.name}",
             notification_type = NotificationType.sucess,
             is_read = False
            )
            db.session.add(student_notification)
            teachers = db.session.query(Teacher).join(TeacherGroup, Teacher.teacher_id == TeacherGroup.teacher_id).filter(TeacherGroup.group_id == current_change_group_request.requested_group_id).all()
            for teacher in teachers:
                teacher_notification = Notification(
                user_id=teacher.user_id,
                title="Student Change Group Request",
                message=f"Student {student.first_name} {student.last_name} group has been changed to {requested_group.name}",
                notification_type=NotificationType.info,
                is_read=False)
                db.session.add(teacher_notification)

            db.session.commit()
    elif status == RequestStatus.rejected:
        current_request.status = RequestStatus.rejected
        current_request.comment = comment
        if request_type == RequestType.section:
            title = "Change Section Request Response"
        elif request_type == RequestType.group:
            title = "Change Group Request Response"
        student_notification = Notification(
            user_id = student.user_id,
             title = title,
             message = "unfortunately, request rejected.",
             notification_type = NotificationType.info,
             is_read = False
        )
        db.session.add(student_notification)
        db.session.commit()

@request_bp.route('/appeal' , methods = ["PATCH"])
def appeal_request():
    data = request.get_json()
    required_fields = ["request_id","student_id","reason"]
    error = run_validations(validate_required_fields(required_fields,data), validate_positive_integer(data["request_id"],"request_id"), validate_positive_integer(data["student_id"],"student_id"))
    if error:
        return jsonify(error),400
    request_id = data["request_id"]
    student_id = data["student_id"]
    reason = data["reason"]
    current_request = Request.query.get(request_id)
    if not current_request:
        return jsonify({"error":"invalid request id"}),400
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error":"invalid student id"}),400
    if current_request.status == RequestStatus.rejected:
        current_request.reason = reason
        current_request.status = RequestStatus.appealed
        student_notification = Notification(
             user_id = student.user_id,
             title = "Request Appeal",
             message = "Request Appeal submitted sucessfully",
             notification_type = NotificationType.sucess,
             is_read = False
            )
        db.session.add(student_notification)
        db.session.commit()
        return jsonify({
  "success": True,
  "message": "Appeal submitted successfully",
  "request_id": request_id
        }),201
    else:
        return jsonify({"error": "cannot appeal a non rejected request"}),400
    
@request_bp.route('/cancel' , methods = ["DELETE"])
def cancel_request():
    data = request.get_json()
    error = run_validations(validate_required_fields(["request_id","student_id","type"],data), validate_positive_integer(data["request_id"],"request_id"), validate_positive_integer(data["student_id"],"student_id"))
    if error:
        return jsonify(error),400
    request_id = data["request_id"]
    student_id = data["student_id"]
    request_type = data["type"]
    current_request = Request.query.get(request_id)
    if not current_request:
        return jsonify({"error": "invalid request id"}),400
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "invalid student id"}),400
    request_type = request_type.lower()
    try:
        RequestType(request_type)
    except ValueError:
        return jsonify({"error": "invalid request type"}),400
    if request_type == RequestType.group:
        if db.session.query(ChangeGroupRequest).filter(ChangeGroupRequest.request_id == request_id).first():
            db.session.query(ChangeGroupRequest).filter(ChangeGroupRequest.request_id == request_id).delete()
    elif request_type == RequestType.section:
        if db.session.query(ChangeSectionRequest).filter(ChangeSectionRequest.request_id == request_id).first():
            db.session.query(ChangeSectionRequest).filter(ChangeSectionRequest.request_id == request_id).delete()
    elif request_type == RequestType.swap:
        if db.session.query(SwapGroupRequest).filter(SwapGroupRequest.request_id == request_id).first():
            db.session.query(SwapGroupRequest).filter(SwapGroupRequest.request_id == request_id).delete()
        elif db.session.query(SwapSectionRequest).filter(SwapSectionRequest.request_id == request_id).first():
            db.session.query(SwapSectionRequest).filter(SwapSectionRequest.request_id == request_id).delete()
    db.session.delete(current_request)
    student_notification = Notification(
             user_id = student.user_id,
             title = "Request Cancel",
             message = "Request canceled sucessfully",
             notification_type = NotificationType.sucess,
             is_read = False
            )
    db.session.add(student_notification)
    db.session.commit()
    return jsonify({
  "success": True,
  "message": "Request canceled successfully"
    }),200

    

    
        






            



    
