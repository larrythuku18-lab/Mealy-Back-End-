from flask import Blueprint, request, jsonify, g

from config import db
from models import User
from routes.auth import auth_required

user_bp = Blueprint('user', __name__)


@user_bp.route('/profile', methods=['GET'])
@auth_required
def profile():
    return jsonify({'user': g.current_user.to_dict()}), 200


@user_bp.route('/profile', methods=['PUT'])
@auth_required
def update_profile():
    data = request.get_json()
    user = g.current_user

    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        # Check uniqueness
        existing = User.query.filter(User.email == data['email'], User.id != user.id).first()
        if existing:
            return jsonify({'error': 'Email already in use'}), 409
        user.email = data['email']
    if 'phone' in data:
        user.phone = data['phone']
    if 'address' in data:
        user.address = data['address']

    db.session.commit()

    return jsonify({
        'user': user.to_dict(),
        'message': 'Profile updated successfully'
    }), 200
