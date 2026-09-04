from datetime import datetime, timezone
from config import db


class Order(db.Model):
    """Customer order with status tracking."""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(32), nullable=False, default='confirmed')
    # Status flow: confirmed -> preparing -> in_transit -> delivered
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    date = db.Column(db.Date, nullable=False, default=lambda: datetime.now(timezone.utc).date())

    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_items=False):
        result = {
            'id': f'ORD-{self.id:03d}',
            'status': self.status,
            'date': self.date.isoformat() if self.date else None,
            'total': self.total_amount,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }
        if include_items:
            result['meals'] = [item.to_dict() for item in self.items]
        return result

    def to_admin_dict(self):
        """Simplified dict for admin today's orders view."""
        first_item = self.items[0] if self.items else None
        meal_option_name = first_item.meal_option.name if first_item and first_item.meal_option else 'N/A'
        return {
            'id': self.id,
            'customerName': self.user.name if self.user else 'Unknown',
            'mealOptionName': meal_option_name,
            'price': self.total_amount,
            'status': self.status,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }


class OrderItem(db.Model):
    """Individual item within an order."""
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    meal_option_id = db.Column(db.Integer, db.ForeignKey('meal_options.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False, default=0.0)

    # Relationships
    meal_option = db.relationship('MealOption', lazy=True)

    def to_dict(self):
        return {
            'name': self.meal_option.name if self.meal_option else 'Unknown',
            'quantity': self.quantity,
            'price': self.price,
            'image': None,  # Frontend handles images via URL if needed
        }
