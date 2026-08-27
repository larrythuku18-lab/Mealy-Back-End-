from datetime import datetime, timezone
from config import db


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)

    # Links payment to the order and user
    order_id = db.Column(
        db.Integer,
        db.ForeignKey('orders.id'),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    # Payment information
    amount = db.Column(db.Float, nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)

    # pending, completed, failed
    status = db.Column(
        db.String(20),
        nullable=False,
        default='pending'
    )

    # M-Pesa transaction information
    mpesa_receipt_number = db.Column(
        db.String(100),
        nullable=True
    )

    checkout_request_id = db.Column(
        db.String(100),
        nullable=True,
        unique=True
    )

    merchant_request_id = db.Column(
        db.String(100),
        nullable=True
    )

    transaction_date = db.Column(
        db.DateTime,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    order = db.relationship(
        'Order',
        backref='payment',
        lazy=True
    )

    user = db.relationship(
        'User',
        backref='payments',
        lazy=True
    )

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'user_id': self.user_id,
            'amount': self.amount,
            'phone_number': self.phone_number,
            'status': self.status,
            'mpesa_receipt_number': self.mpesa_receipt_number,
            'checkout_request_id': self.checkout_request_id,
            'merchant_request_id': self.merchant_request_id,
            'transaction_date': (
                self.transaction_date.isoformat()
                if self.transaction_date else None
            ),
            'created_at': (
                self.created_at.isoformat()
                if self.created_at else None
            ),
            'updated_at': (
                self.updated_at.isoformat()
                if self.updated_at else None
            ),
        }