from datetime import date
from flask import Blueprint, request, jsonify, g

from config import db
from models import Order, OrderItem, MealOption
from routes.auth import auth_required, role_required
from errors import bad_request, unauthorized, not_found
from validators import get_json_or_400, validate_order_status

order_bp = Blueprint('order', __name__)


@order_bp.route('/today', methods=['GET'])
@role_required('admin')
def todays_orders():
    """Admin view: get all of today's orders with customer names."""
    today = date.today()
    orders = Order.query.filter_by(date=today).order_by(Order.created_at.desc()).all()
    return jsonify({
        'orders': [o.to_admin_dict() for o in orders]
    }), 200


@order_bp.route('/', methods=['GET'])
@auth_required
def list_orders():
    """Customer view: list the current user's orders."""
    user_id = g.current_user.id
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    return jsonify({
        'orders': [o.to_dict(include_items=True) for o in orders]
    }), 200


@order_bp.route('/', methods=['POST'])
@auth_required
def create_order():
    """Create a new order from the customer's cart."""
    data = request.get_json()

    meal_option_ids = data.get('mealOptionIds', [])
    quantities = data.get('quantities', [])

    if not meal_option_ids or not quantities or len(meal_option_ids) != len(quantities):
        return bad_request('mealOptionIds and quantities are required and must match')

    total_amount = 0
    items_to_add = []

    for meal_id, quantity in zip(meal_option_ids, quantities):
        meal_option = db.session.get(MealOption, meal_id)
        if not meal_option:
            return not_found(f'Meal option {meal_id} not found')

        total_amount += meal_option.price * quantity
        items_to_add.append({
            'meal_option_id': meal_id,
            'quantity': quantity,
            'price': meal_option.price,
        })

    order = Order(
        user_id=g.current_user.id,
        total_amount=total_amount,
        status='confirmed',
        date=date.today(),
    )
    db.session.add(order)
    db.session.flush()

    for item_data in items_to_add:
        order_item = OrderItem(order_id=order.id, **item_data)
        db.session.add(order_item)

    db.session.commit()

    return jsonify({
        'message': 'Order created successfully',
        'order': order.to_dict(include_items=True)
    }), 201


@order_bp.route('/<int:order_id>', methods=['GET'])
@auth_required
def get_order(order_id):
    """Get a specific order (customer can only view their own)."""
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    if order.user_id != g.current_user.id and g.current_user.role != 'admin':
        return unauthorized('You can only view your own orders')

    return jsonify({'order': order.to_dict(include_items=True)}), 200


@order_bp.route('/<int:order_id>/status', methods=['PUT'])
@role_required('admin')
def update_order_status(order_id):

    data, err = get_json_or_400()
    if err:
        return err

    new_status = data.get('status')
    ok, status_err = validate_order_status(new_status)
    if not ok:
        return status_err

    order = db.session.get(Order, order_id)
    if not order:
        return not_found('Order not found')

    order.status = new_status
    db.session.commit()

    return jsonify({
        'message': 'Order status updated',
        'order': order.to_dict(include_items=True)
    }), 200
