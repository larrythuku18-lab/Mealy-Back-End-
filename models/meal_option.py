from datetime import datetime, timezone
from config import db


class MealOption(db.Model):
    """Admin-managed meal options that can be selected for daily menus."""
    __tablename__ = 'meal_options'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False, default=0.0)
    caterer_id = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'catererId': self.caterer_id,
        }
