from datetime import datetime, timezone
from config import db


class Royalty(db.Model):
    """Royalty record tied to an order."""
    __tablename__ = 'royalties'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    period = db.Column(db.String(64), nullable=True)
    paid = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships
    order = db.relationship('Order', backref='royalties', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'order_id': self.order_id,
            'amount': self.amount,
            'period': self.period,
            'paid': self.paid,
        }
