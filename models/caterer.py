from datetime import datetime, timezone
from config import db


class Caterer(db.Model):
    """Represents a food caterer/business."""

    __tablename__ = 'caterers'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        nullable=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    business_name = db.Column(
        db.String(150),
        nullable=True
    )

    description = db.Column(
        db.Text,
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

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'businessName': self.business_name,
            'description': self.description,
            'createdAt': (
                self.created_at.isoformat()
                if self.created_at else None
            ),
            'updatedAt': (
                self.updated_at.isoformat()
                if self.updated_at else None
            )
        }