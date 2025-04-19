from flask import Blueprint, jsonify, request
from models import (
    db,
    ChangeGroupRequest, ChangeSectionRequest, SwapGroupRequest, SwapSectionRequest, 
    Student, Group, Section, Request, Staff,
    Notification
)
from resources.validations import *
from datetime import datetime

from sqlalchemy import in_

from enum import Enum

class request_type(Enum):
    GROUP = "group"
    SECTION = "section"
    SWAP = "swap"

class request_status(Enum):
    PENDING: "pending"
    APPROVED: "approved"
    REJECTED: "rejected"
    APPEALED: "appealed"
    ALL: "all"

class request_urgency(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class notification_type(Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    

request_bp = Blueprint('request_bp', __name__)

def validate_request_type(request_type):
    try:
        request_type(request_type)
        return None
    except ValueError:
        return {"error": "Invalid request type"}

def validate_request_status(request_status):
    try:
        request_status(request_status)
        return None
    except ValueError:
        return {"error": "Invalid request status"}

def validate_request_urgency(request_urgency):
    try:
        int_request_urgency = int(request_urgency)
        request_urgency(int_request_urgency)
        return None
    except ValueError:
        return {"error": "Invalid Urgency"}
        
@request_bp.route('/', methods=["GET"])
def get_requests():
    # filters
    search_data = request.args.get("search_data", type=str)
    page = request.args.get("page", default=1, type=int)
    page_size = request.args.get("page_size", default=10, type=int)
    student_id = request.args.get("student_id", type=int)
    status = request.args.get("status", type=str)
    request_type = request.args.get("type", type=str)
    urgency = request.args.get("urgency", type=int)
    start_date = request.args.get("start_date", type=str)
    end_date = request.args.get("end_date", type=str)
    
    requests = db.session.query(select(Request, Student)).join(Student, Request.student_id == Student.student_id)
    
    
    if search_data:
        try:
            search_id = int(search_data)
            requests = requests.filter(Request.request_id == search_id)
        except ValueError:
            requests = requests.filter(Student.last_name.ilike(f"%{search_data}%"))
            
    if student_id:
        error = validate_positive_integer(student_id, "student_id")
        if error: return jsonify(error), 400
        requests = requests.filter(Request.student_id == student_id)
        
    if status:
        error = validate_request_status(status)
        if error: return jsonify(error), 400
        requests = requests.filter(Request.status == status)
        
    if urgency:
        error = validate_request_urgency(urgency)
        if error: return jsonify(error), 400
        requests = requests.filter(Request.urgency == urgency)
        
    if request_type:
        error = validate_request_type(request_type)
        if error: return jsonify(error), 400
        requests = requests.filter(Request.request_type == request_type)
        
    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        requests = requests.filter(Request.created_at >= start_date)
        
    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        requests = requests.filter(Request.created_at <= end_date)
        
    
    # order result
    requests = requests.order_by(desc(Request.created_at))
    
    # Pagination
    requests = requests.paginate(page=page, per_page=page_size)
    
    return jsonify({
        "success": True,
        "data": [request.to_dict() for request in requests],
        "pagination": {
            "totalItems": requests.total,
            "currentPage": requests.page,
            "pageSize": requests.per_page,
            "totalPages": requests.pages,
        }
    }), 200

@request_bp.route('/<int:request_id>', methods=["GET"])
def get_request(request_id):
    
    swap_type = request.args.get("type") # it has to be section or group (it is used to know which swap type)
    if swap_type:
        if swap_type not in ["group", "section"]:
            return jsonify({"error": "Invalid request type"}), 404
    
    request = Request.query.get(request_id)
    if not request:
        return jsonify({"error": "Request not found"}), 404
    
    # validate if request type exist
    error = validate_request_type(request.request_type)
    if error:
        return jsonify(error), 400
    
    
    if request.request_type == request_type.GROUP.value:
        request = request.join(ChangeGroupRequest, ChangeGroupRequest.request_id == Request.request_id).first()
    elif request.request_type == request_type.SECTION.value:
        request = request.join(ChangeSectionRequest, ChangeSectionRequest.request_id == Request.request_id).first()
    elif request.request_type == request_type.SWAP.value:
        if swap_type == "group":
            request = request.join(SwapGroupRequest, SwapGroupRequest.request_id == Request.request_id).first()
        elif swap_type == "section":
            request = request.join(SwapSectionRequest, SwapSectionRequest.request_id == Request.request_id).first()
            
    
    
    return jsonify({
        "success": True,
        "data": request.to_dict()
    }), 200

@request_bp.route('/change', methods=["POST"])
def create_change_request():
    data = request.get_json()
    
    requestType = request.args.get("type")
    
    if requestType:
        error = validate_request_type(requestType)
        if error:
            return jsonify(error), 400
        
    
    required_fields = ["student_id", "reason", "urgency", "requested_id"]
    error = run_validations([
        (validate_required_fields, [required_fields, data]),
        (validate_positive_integer, [data["student_id"], "student_id"]),
        (validate_request_urgency, data["urgency"]),
        (validate_positive_integer, [data["requested_id"], "requested_id"])
    ])
    if error:
        return jsonify(error), 400
    
    # check if the user already has an active request of the same type
    active_request = Request.query.filter_by(
        student_id=data["student_id"],
        request_type=requestType
    ).filter(Request.status.in_(['pending', 'appealed'])).first()

    if active_request:
        return jsonify({
            "error": "You already have an active request of this type. Please wait for it to be processed."
        }), 400
        
    student = Student.query.get(data["student_id"])
    if not student:
        return jsonify({"error": "Invalid student"}), 400
    
    if requestType == request_type.GROUP.value:
        
        requested_group = Group.query.get(data["requested_id"])
        if not requested_group:
            return jsonify({"error": "Invalid group"}), 400
        
        new_request = Request(
            student_id=data["student_id"],
            status="pending",
            reason=data["reason"],
            urgency=data["urgency"],
            request_type=request_type.GROUP.value
        )
            
        db.session.add(new_request)
        db.session.commit()
        
        if requested_group.group_type == "tutorial":
            new_change_group_request = ChangeGroupRequest(
                request_id=new_request.request_id,
                current_group_id=student.tutorial_group_id,
                requested_group_id=requested_group.group_id
            )
        elif requested_group.group_type == "lab":
            new_change_group_request = ChangeGroupRequest(
                request_id=new_request.request_id,
                current_group_id=student.lab_group_id,
                requested_group_id=requested_group.group_id
            )
            
        db.session.add(new_change_group_request)
        db.session.commit()


    elif requestType == request_type.SECTION.value:
        requested_section = Section.query.get(data["requested_id"])
        
        if not requested_section:
            return jsonify({"error": "Invalid Section"}), 400

        
        new_request = Request(
            student_id=data["student_id"],
            status="pending",
            reason=data["reason"],
            urgency=data["urgency"],
            request_type=request_type.SECTION.value
        )
        db.session.add(new_request)
        db.session.commit()
        
        new_change_section_request = ChangeSectionRequest(
            request_id=new_request.request_id,
            current_section_id=student.section_id,
            requested_section_id=requested_section.section_id
        )
        db.session.add(new_change_section_request)
        db.session.commit()



    return jsonify({
        "success": True,
        "message": "Change request created successfully",
        "request": new_request.to_dict()
    }), 201

@request_bp.route('/change/status' , methods = ["PUT"])
def review_request():
    data = request.get_json()
    
    required_fields = ["request_id", "status", "type", "comment"]
    error = run_validations([
        (validate_required_fields, [required_fields,data]),
        (validate_positive_integer, [data["request_id"],"request_id"]),
    ])
    if error:
        return jsonify(error), 400
    
    error = validate_request_status(data["status"])
    if error:
        return jsonify(error), 400
    
    request = Request.query.get(data["request_id"])
    if not request:
        return jsonify({"error":"request id not found"}),400

    if data["status"] == request_status.APPROVED.value:
        # update request
        request.status = request_status.APPROVED.value
        db.session.commit()
        
        if request.request_type == request_type.GROUP.value:
            change_group_request = db.session.query(select(ChangeGroupRequest).filter(ChangeGroupRequest.request_id == request.request_id)).first()
            
            student = Student.query.get(request.student_id)
            requested_group = Group.query.get(change_group_request.requested_group_id)
            
            if requested_group.group_type == "tutorial":
                student.tutorial_group_id = change_group_request.requested_group_id
            elif requested_group.group_type == "lab":
                student.lab_group_id = change_group_request.requested_group_id

            db.session.commit()
            
            # create notification for student
            student_notification = Notification(
                user_id = student.student_id,
                title = "Change Group Request Response",
                message = "request approved, you have been moved!",
                notification_type = notification_type.SUCCESS.value,
                is_read = False
            )
            db.session.add(student_notification)
            db.session.commit()
        elif request.request_type == request_type.SECTION.value:
            change_section_request = db.session.query(select(ChangeSectionRequest).filter(ChangeSectionRequest.request_id == request.request_id)).first()

            student = Student.query.get(request.student_id)
            requested_section = Section.query.get(change_section_request.requested_section_id)
            
            student.section_id = change_section_request.requested_section_id
            
            db.session.commit()
            
            # create notification for student
            student_notification = Notification(
                user_id = student.student_id,
                title = "Change Section Request Response",
                message = "request approved, you have been moved!",
                notification_type = notification_type.SUCCESS.value,
                is_read = False
            )
            db.session.add(student_notification)
            
            db.session.commit()
            
    elif data["status"] == request_status.REJECTED.value:
        # update request
        request.status = request_status.REJECTED.value
        db.session.commit()
        
        if request.request_type == request_type.GROUP.value:
            # create notification for student
            student = Student.query.get(request.student_id)
            student_notification = Notification(
                user_id = student.student_id,
                title = "Change Group Request Response",
                message = "request rejected.",
                notification_type = notification_type.WARNING.value,
                is_read = False
            )
            db.session.add(student_notification)
            db.session.commit()
        elif request.request_type == request_type.SECTION.value:
            # create notification for student
            student = Student.query.get(request.student_id)
            student_notification = Notification(
                user_id = student.student_id,
                title = "Change Section Request Response",
                message = "request appealed.",
                notification_type = notification_type.WARNING.value,
                is_read = False
            )
            db.session.add(student_notification)
            db.session.commit()
        
    return {
        "success": True,
        "data": request.to_dict()
    }

@request_bp.route('/appeal', methods=["POST"])
def appeal_request():
    data = request.get_json()

    # Validate required fields
    required_fields = ["requestId", "studentId", "reason"]
    error = run_validations([
        (validate_required_fields, [required_fields, data]),
        (validate_positive_integer, [data["requestId"], "requestId"]),
        (validate_positive_integer, [data["studentId"], "studentId"])
    ])
    if error:
        return jsonify(error), 400

    # Fetch the request
    request_id = data["requestId"]
    student_id = data["studentId"]
    reason = data["reason"]

    current_request = Request.query.get(request_id)
    if not current_request:
        return jsonify({"error": "Invalid request ID"}), 404

    # Validate the student
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Invalid student ID"}), 404

    # Update the request status and reason
    current_request.status = request_status.APPEALED.value
    current_request.reason = reason
    db.session.commit()

    # Generate a notification for administrators
    staffs = Staff.query.all()
    for staff in staffs:
        admin_notification = Notification(
            user_id=staff.staff_id,  # Assuming admin notifications are broadcasted
            title="Request Appeal Submitted",
            message=f"Student {student.first_name} {student.last_name} has appealed request ID {request_id}.",
            notification_type=notification_type.INFO.value,
            is_read=False
        )
        db.session.add(admin_notification)
        db.session.commit()

    return jsonify({
        "success": True,
        "message": "Appeal submitted successfully",
        "requestId": request_id
    }), 201

@request_bp.route('/cancel', methods=["POST"])
def cancel_request():
    data = request.get_json()

    # Validate required fields
    required_fields = ["requestId", "studentId"]
    error = run_validations([
        (validate_required_fields, [required_fields, data]),
        (validate_positive_integer, [data["requestId"], "requestId"]),
        (validate_positive_integer, [data["studentId"], "studentId"])
    ])
    if error:
        return jsonify(error), 400

    # Fetch the request
    request_id = data["requestId"]
    student_id = data["studentId"]

    current_request = Request.query.get(request_id)
    if not current_request:
        return jsonify({"error": "Invalid request ID"}), 404

    # Ensure the request is in 'pending' status
    if current_request.status != request_status.PENDING.value:
        return jsonify({"error": "Only pending requests can be canceled"}), 400

    # Delete the request
    db.session.delete(current_request)
    db.session.commit()

    # Create a notification for the student
    student_notification = Notification(
        user_id=student_id,
        title="Request Canceled",
        message=f"Your request with ID {request_id} has been canceled successfully.",
        notification_type=notification_type.SUCCESS.value,
        is_read=False
    )
    db.session.add(student_notification)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Request canceled successfully"
    }), 200

@request_bp.route('/swap', methods=["GET"])
def get_swap_requests():
    # filters
    search_data = request.args.get("search_data", type=str)
    page = request.args.get("page", default=1, type=int)
    page_size = request.args.get("page_size", default=10, type=int)
    student_id = request.args.get("student_id", type=int)
    status = request.args.get("status", type=str)
    urgency = request.args.get("urgency", type=int)
    start_date = request.args.get("start_date", type=str)
    end_date = request.args.get("end_date", type=str)
    opportunity = request.args.get("opportunity", default="false", type=str).lower() == "true"

    if not student_id:
        return jsonify({"error": "student_id is required"}), 400


    swap_group_query = db.session.query(
        SwapGroupRequest.swap_group_request_id.label("swap_request_id"),
        Request.request_id,
        Request.student_id,
        Student.first_name.label("student_name"),
        Request.status,
        Request.urgency,
        Request.created_at,
        Request.updated_at,
        Group.group_name.label("current_group"),
        None.label("current_section"),  # Placeholder for section
        Group.group_id.label("current_group_id"),
        None.label("current_section_id"),  # Placeholder for section
        None.label("requested_group"),  # Placeholder for requested group
        None.label("requested_section"),  # Placeholder for requested section
        SwapGroupRequest.requested_student_id
    ).join(Request, SwapGroupRequest.request_id == Request.request_id) \
     .join(Student, Request.student_id == Student.student_id) \
     .join(Group, SwapGroupRequest.current_group_id == Group.group_id)

    swap_section_query = db.session.query(
        SwapSectionRequest.swap_section_request_id.label("swap_request_id"),
        Request.request_id,
        Request.student_id,
        Student.first_name.label("student_name"),
        Request.status,
        Request.urgency,
        Request.created_at,
        Request.updated_at,
        None.label("current_group"),  # Placeholder for group
        Section.section_name.label("current_section"),
        None.label("current_group_id"),  # Placeholder for group
        Section.section_id.label("current_section_id"),
        None.label("requested_group"),  # Placeholder for requested group
        None.label("requested_section"),  # Placeholder for requested section
        SwapSectionRequest.requested_student_id
    ).join(Request, SwapSectionRequest.request_id == Request.request_id) \
     .join(Student, Request.student_id == Student.student_id) \
     .join(Section, SwapSectionRequest.current_section_id == Section.section_id)

    combined_query = swap_group_query.union_all(swap_section_query)

    # Apply filters
    if search_data:
        combined_query = combined_query.filter(
            (Student.first_name.ilike(f"%{search_data}%")) |
            (Student.last_name.ilike(f"%{search_data}%")) |
            (Request.student_id == search_data)
        )
    if status:
        combined_query = combined_query.filter(Request.status == status)
    if urgency:
        combined_query = combined_query.filter(Request.urgency == urgency)
    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        combined_query = combined_query.filter(Request.created_at >= start_date)
    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        combined_query = combined_query.filter(Request.created_at <= end_date)

    if opportunity:
        combined_query = combined_query.filter(SwapGroupRequest.requested_student_id == None)

    combined_query = combined_query.order_by(Request.created_at.desc())


    total_items = combined_query.count()
    paginated_query = combined_query.limit(page_size).offset((page - 1) * page_size).all()

    data = [
        {
            "swap_request_id": row.swap_request_id,
            "request_id": row.request_id,
            "student_id": row.student_id,
            "student_name": row.student_name,
            "status": row.status,
            "urgency": row.urgency,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
            "current_group": row.current_group,
            "current_section": row.current_section,
            "current_group_id": row.current_group_id,
            "current_section_id": row.current_section_id,
            "requested_group": row.requested_group,
            "requested_section": row.requested_section,
            "requested_student_id": row.requested_student_id
        }
        for row in paginated_query
    ]

    return jsonify({
        "success": True,
        "data": data,
        "pagination": {
            "totalItems": total_items,
            "currentPage": page,
            "pageSize": page_size,
            "totalPages": (total_items + page_size - 1) // page_size
        }
    }), 200

@request_bp.route('/swap', methods=["POST"])
def create_swap_request():
    data = request.get_json()

    required_fields = ["requesting_student_id", "requested_id", "reason", "urgency", "swap_type"]
    
    error = run_validations([
        (validate_required_fields, [required_fields, data]),
        (validate_positive_integer, [data["requesting_student_id"], "requesting_student_id"]),
        (validate_positive_integer, [data["group_id"], "groupId"]),
        (validate_request_urgency, data["urgency"])
    ])
    if error:
        return jsonify(error), 400
    
    # check if the user already has an active request of the same type
    active_request = Request.query.filter_by(
        student_id=data["student_id"],
        request_type=requestType
    ).filter(Request.status.in_(['pending', 'appealed'])).first()
    
    if active_request:
        return jsonify({
            "error": "You already have an active request of this type. Please wait for it to be processed."
        }), 400
        
    student = Student.query.get(data["student_id"])
    if not student:
        return jsonify({"error": "Invalid student"}), 400
    
    if data["swap_type"] == request_type.GROUP.value:
        requested_group = Group.query.get(data["requested_id"])
        if not requested_group:
            return jsonify({"error": "Invalid group"}), 400
        
        new_request = Request(
            student_id=data["student_id"],
            status="pending",
            reason=data["reason"],
            urgency=data["urgency"],
            request_type=request_type.GROUP.value
        )
            
        db.session.add(new_request)
        db.session.commit()
        
        new_swap_group_request = SwapGroupRequest(
            request_id=new_request.request_id,
            current_student_id=student.student_id,
            requested_student_id=None
        )
            
        db.session.add(new_swap_group_request)
        db.session.commit()
    
    elif data["swap_type"] == request_type.SECTION.value:
        requested_section = Section.query.get(data["requested_id"])
        if not requested_section:
            return jsonify({"error": "Invalid Section"}), 400
        
        new_request = Request(
            student_id=data["student_id"],
            status="pending",
            reason=data["reason"],
            urgency=data["urgency"],
            request_type=request_type.SECTION.value
        )
        
        db.session.add(new_request)
        db.session.commit()
        
        new_swap_section_request = SwapSectionRequest(
            request_id=new_request.request_id,
            current_student_id=student.student_id,
            requested_student_id=None
        )
        
    return jsonify({
        "success": True,
        "message": "Swap request submitted successfully",
        "requestId": new_request.request_id
    }), 201
   
@request_bp.route('/swap', methods=["PATCH"])
def update_swap_request():
    data = request.get_json()
    
    required_fields = ["swap_request_id", "responding_student_id", "response", "opportunity", "type"]
    error = run_validations([
        (validate_required_fields, [required_fields, data]),
        (validate_positive_integer, [data["swap_request_id"], "swap_request_id"]),
        (validate_positive_integer, [data["responding_student_id"], "responding_student_id"]),
    ])
    
    if data["type"] == request_type.GROUP.value:
        swap_request = SwapGroupRequest.query.get(data["swap_request_id"])
    elif data["type"] == request_type.SECTION.value:
        swap_request = SwapSectionRequest.query.get(data["swap_request_id"])
        
    if not swap_request:
        return jsonify({"error": "Invalid swap request ID"}), 404

    responding_student = Student.query.get(data["responding_student_id"])
    if not responding_student:
        return jsonify({"error": "Invalid responding student ID"}), 404
    
    request = Request.query.get(swap_request.request_id)
    
    if data["response"] == "reject":
        request.status = request_status.REJECTED.value
        db.session.commit()
        
        notification = Notification(
            user_id=request.student_id,
            title="Swap Request Rejected",
            message=f"Your swap request with ID {data["swap_request_id"]} has been rejected.",
            notification_type=notification_type.WARNING.value,
            is_read=False
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Swap request rejected successfully",
            "request": base_request.to_dict()
        }), 200
        
    if data["response"] == "accept":
        request.status = request_status.APPROVED.value
        db.session.commit()
        
        if opportunity:
            if swap_request.requested_student_id is not None:
                return jsonify({"error": "This is not an open opportunity"}), 400
            swap_request.requested_student_id = data["responding_student_id"]
            
        requesting_student = Student.query.get(base_request.student_id)
        if not requesting_student:
            return jsonify({"error": "Requesting student not found"}), 404
    
        if data["type"] == request_type.GROUP.value:
            tmp_tutorial = requesting_student.tutorial_group_id
            tmp_lab = requesting_student.lab_group_id

            requesting_student.tutorial_group_id = responding_student.tutorial_group_id
            requesting_student.lab_group_id = responding_student.lab_group_id

            responding_student.tutorial_group_id = tmp_tutorial
            responding_student.lab_group_id = tmp_lab

        elif data["type"] == request_type.SECTION.value:
            tmp_section = requesting_student.section_id
            requesting_student.section_id = responding_student.section_id
            responding_student.section_id = tmp_section

            tmp_tutorial = requesting_student.tutorial_group_id
            tmp_lab = requesting_student.lab_group_id

            requesting_student.tutorial_group_id = responding_student.tutorial_group_id
            requesting_student.lab_group_id = responding_student.lab_group_id

            responding_student.tutorial_group_id = tmp_tutorial
            responding_student.lab_group_id = tmp_lab
    
        db.session.commit()
        
        # Notify both students
        requesting_student_notification = Notification(
            user_id=requesting_student.student_id,
            title="Swap Request Accepted",
            message=f"Your swap request with ID {data["swap_request_id"]} has been accepted. Your group has been updated.",
            notification_type=notification_type.SUCCESS.value,
            is_read=False
        )
        responding_student_notification = Notification(
            user_id=responding_student.student_id,
            title="Swap Request Accepted",
            message=f"You have accepted a swap request with ID {data["swap_request_id"]}. Your group has been updated.",
            notification_type=notification_type.SUCCESS.value,
            is_read=False
        )
        db.session.add(requesting_student_notification)
        db.session.add(responding_student_notification)

        # Notify relevant teachers
        teachers = Staff.query.filter_by(role="teacher").all()
        for teacher in teachers:
            teacher_notification = Notification(
                user_id=teacher.user_id,
                title="Swap Request Completed",
                message=f"A swap request with ID {data["swap_request_id"]} has been completed. Please review the updated group assignments.",
                notification_type=notification_type.INFO.value,
                is_read=False
            )
            db.session.add(teacher_notification)

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Swap request accepted successfully",
            "request": base_request.to_dict()
        }), 200
        
@request_bp.route('/swap/verify', methods=["GET"])
def verify_swap_eligibility():
    student_id = request.args.get("student_id", type=int)
    student_request_id = request.args.get("student_request_id", type=int)

    if not student_id or not student_request_id:
        return jsonify({"error": "Both student_id and student_request_id are required"}), 400

    student = Student.query.get(student_id)
    requested_student = Student.query.get(student_request_id)

    if not student:
        return jsonify({"error": "Invalid student_id"}), 404
    if not requested_student:
        return jsonify({"error": "Invalid student_request_id"}), 404

    if student.speciality_id == requested_student.speciality_id:
        return jsonify({
            "success": True,
            "eligible": True,
            "reason": "Students are in the same specialty"
        }), 200

    # if not eligible
    return jsonify({
        "success": True,
        "eligible": False,
        "reason": "Students are not in the same specialty or year"
    }), 200





