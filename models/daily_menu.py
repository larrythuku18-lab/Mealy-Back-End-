from datetime import datetime, date, timezone
import json

from config import db


class DailyMenu(db.Model):
    """Represents a menu for a specific caterer and date."""

    __tablename__ = 'daily_menus'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    caterer_id = db.Column(
        db.Integer,
        db.ForeignKey('caterers.id'),
        nullable=True
    )

    date = db.Column(
        db.Date,
        nullable=False,
        default=date.today
    )

    is_published = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    # Stores meal option IDs as a JSON array
    meal_option_ids = db.Column(
        db.Text,
        nullable=False,
        default='[]'
    )

    # Relationship with Caterer
    caterer = db.relationship(
        'Caterer',
        backref='daily_menus',
        lazy=True
    )
    
    __table_args__ = (
      db.UniqueConstraint(
        'caterer_id',
        'date',
        name='unique_caterer_menu_date'
      ),
    )

    def get_meal_option_ids(self):
        """Return meal option IDs from the stored JSON."""
        return (
            json.loads(self.meal_option_ids)
            if self.meal_option_ids
            else []
        )

    def set_meal_option_ids(self, ids):
        """Store meal option IDs as JSON."""
        self.meal_option_ids = json.dumps(ids)

    def to_dict(self):
        return {
            'id': self.id,
            'catererId': self.caterer_id,
            'date': (
                self.date.isoformat()
                if self.date
                else None
            ),
            'isPublished': self.is_published,
            'mealOptionIds': self.get_meal_option_ids(),
        }