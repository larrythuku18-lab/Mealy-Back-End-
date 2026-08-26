from datetime import datetime, timezone
from config import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(32), nullable=True)
    role = db.Column(db.String(32), nullable=False, default='user')  # 'user' | 'admin'
    caterer_id = db.Column(db.String(128), nullable=True)
    address = db.Column(db.String(256), nullable=True)
    joined_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships
    orders = db.relationship('Order', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    royalties = db.relationship('Royalty', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'catererId': self.caterer_id,
            'address': self.address,
            'joinedDate': self.joined_date.isoformat() if self.joined_date else None,
        }
