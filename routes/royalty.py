from flask import Blueprint, request, jsonify, g

from config import db
from models import Royalty, Order
from routes.auth import auth_required
from errors import bad_request, unauthorized, not_found
from validators import get_json_or_400, validate_required_fields

royalty_bp = Blueprint('royalty', __name__)


@royalty_bp.route('/', methods=['POST'])
@auth_required
def create_royalty():
    data, err = get_json_or_400()
    if err:
        return err

    ok, field_err = validate_required_fields(data, ['order_id', 'amount'])
    if not ok:
        return field_err

    order_id = data.get('order_id')
    amount = data.get('amount')
    period = data.get('period')

    order = db.session.get(Order, order_id)
    if not order:
        return not_found('Order not found')

    # Check if user owns this order
    if order.user_id != g.current_user.id:
        return unauthorized('You can only create royalties for your own orders')

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
        return not_found('Royalty not found')

    if royalty.user_id != g.current_user.id and g.current_user.role != 'admin':
        return unauthorized('You can only view your own royalties')

    return jsonify({'royalty': royalty.to_dict()}), 200


@royalty_bp.route('/', methods=['GET'])
@auth_required
def list_royalties():
    royalties = Royalty.query.filter_by(user_id=g.current_user.id).all()
    return jsonify({
        'royalties': [r.to_dict() for r in royalties]
    }), 200
