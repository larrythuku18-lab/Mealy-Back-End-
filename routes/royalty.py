from flask import Blueprint, request, jsonify, g

from config import db
from models import Royalty, Order
from routes.auth import auth_required

royalty_bp = Blueprint('royalty', __name__)


@royalty_bp.route('/', methods=['POST'])
@auth_required
def create_royalty():
    data = request.get_json()
    order_id = data.get('order_id')
    amount = data.get('amount')
    period = data.get('period')

    if not order_id or amount is None:
        return jsonify({'error': 'order_id and amount are required'}), 400

    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    # Check if user owns this order
    if order.user_id != g.current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    royalty = Royalty(
        user_id=g.current_user.id,
        order_id=order_id,
        amount=float(amount),
        period=period,
    )
    db.session.add(royalty)
    db.session.commit()

    return jsonify({
        'message': 'Royalty record created successfully',
        'royalty': royalty.to_dict()
    }), 201


@royalty_bp.route('/<int:royalty_id>', methods=['GET'])
@auth_required
def get_royalty(royalty_id):
    royalty = db.session.get(Royalty, royalty_id)
    if not royalty:
        return jsonify({'error': 'Royalty not found'}), 404

    if royalty.user_id != g.current_user.id and g.current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify({'royalty': royalty.to_dict()}), 200


@royalty_bp.route('/', methods=['GET'])
@auth_required
def list_royalties():
    royalties = Royalty.query.filter_by(user_id=g.current_user.id).all()
    return jsonify({
        'royalties': [r.to_dict() for r in royalties]
    }), 200
