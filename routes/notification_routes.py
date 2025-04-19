from flask import Blueprint, jsonify, request
from models import db, Notification
from resources.validations import *

notification_bp = Blueprint('notification_bp', __name__)

VALID_NOTIFICATION_TYPES = ["info", "success", "warning", "error"]

@notification_bp.route('/', methods=["GET"])
def get_notifications():
    user_id = request.args.get("user_id", type=int)
    page = request.args.get("page", default=1, type=int)
    page_size = request.args.get("page_size", default=10, type=int)
    notif_type = request.args.get("type", type=str)
    read = request.args.get("read", type=str)

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    notifications = Notification.query.filter_by(user_id=user_id)

    if notif_type:
        if notif_type not in VALID_NOTIFICATION_TYPES:
            return jsonify({"error": f"Invalid notification type. Valid types are: {', '.join(VALID_NOTIFICATION_TYPES)}"}), 400
        notifications = notifications.filter_by(notification_type=notif_type)
    if read is not None:
        read = read.lower() == "true"
        notifications = notifications.filter_by(is_read=read)

    notifications = notifications.order_by(Notification.created_at.desc()).paginate(page=page, per_page=page_size)

    return jsonify({
        "success": True,
        "data": [notif.to_dict() for notif in notifications.items],
        "pagination": {
            "totalItems": notifications.total,
            "currentPage": notifications.page,
            "pageSize": notifications.per_page,
            "totalPages": notifications.pages,
        }
    }), 200


@notification_bp.route('/read', methods=["PATCH"])
def mark_notification_as_read():
    notification_id = request.args.get("notification_id", type=int)

    if not notification_id:
        return jsonify({"error": "notification_id is required"}), 400

    notification = Notification.query.get(notification_id)
    if not notification:
        return jsonify({"error": "Notification not found"}), 404

    notification.is_read = True
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Notification marked as read",
        "notification": notification.to_dict()
    }), 200


@notification_bp.route('/read', methods=["DELETE"])
def delete_notification():
    notification_id = request.args.get("notification_id", type=int)

    if not notification_id:
        return jsonify({"error": "notification_id is required"}), 400

    notification = Notification.query.get(notification_id)
    if not notification:
        return jsonify({"error": "Notification not found"}), 404

    db.session.delete(notification)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Notification deleted successfully"
    }), 200


@notification_bp.route('/readall', methods=["PATCH"])
def mark_all_notifications_as_read():
    user_id = request.args.get("user_id", type=int)
    page = request.args.get("page", type=int)
    page_size = request.args.get("page_size", type=int)

    if not user_id or not page or not page_size:
        return jsonify({"error": "user_id, page, and page_size are required"}), 400

    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).paginate(page=page, per_page=page_size)

    for notification in notifications.items:
        notification.is_read = True
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "All notifications on the current page marked as read"
    }), 200


@notification_bp.route('/readall', methods=["DELETE"])
def delete_all_notifications():
    user_id = request.args.get("user_id", type=int)
    page = request.args.get("page", type=int)
    page_size = request.args.get("page_size", type=int)

    if not user_id or not page or not page_size:
        return jsonify({"error": "user_id, page, and page_size are required"}), 400

    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).paginate(page=page, per_page=page_size)

    for notification in notifications.items:
        db.session.delete(notification)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "All notifications deleted successfully"
    }), 200