from datetime import date

from flask import Blueprint, jsonify

from config import db
from models import Order
from routes.auth import role_required


sales_bp = Blueprint('sales', __name__)


@sales_bp.route('/today', methods=['GET'])
@role_required('admin')
def todays_sales():
    """Admin view: get today's total orders and revenue."""

    today = date.today()

    orders = Order.query.filter_by(
        date=today
    ).all()

    total_orders = len(orders)

    total_revenue = sum(
        order.total_amount
        for order in orders
    )

    return jsonify({
        'date': today.isoformat(),
        'total_orders': total_orders,
        'total_revenue': total_revenue
    }), 200