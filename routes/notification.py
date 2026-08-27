from flask import Blueprint, jsonify, g

from config import db
from models import Notification
from routes.auth import auth_required


notification_bp = Blueprint('notification', __name__)


@notification_bp.route('/', methods=['GET'])
@auth_required
def list_notifications():
    """Get notifications for the logged-in customer."""

    notifications = Notification.query.filter_by(
        user_id=g.current_user.id
    ).order_by(
        Notification.created_at.desc()
    ).all()

    return jsonify({
        'notifications': [
            notification.to_dict()
            for notification in notifications
        ]
    }), 200