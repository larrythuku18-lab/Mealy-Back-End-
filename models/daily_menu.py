from datetime import datetime, date, timezone
from config import db


class DailyMenu(db.Model):
    """Represents the published menu for a specific date."""
    __tablename__ = 'daily_menus'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True, default=date.today)
    is_published = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Many-to-many: which meal options are on today's menu
    meal_option_ids = db.Column(db.Text, nullable=False, default='[]')  # JSON array of IDs

    def get_meal_option_ids(self):
        """Parse the JSON-stored meal option IDs."""
        import json
        return json.loads(self.meal_option_ids) if self.meal_option_ids else []

    def set_meal_option_ids(self, ids):
        """Store meal option IDs as JSON."""
        import json
        self.meal_option_ids = json.dumps(ids)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'isPublished': self.is_published,
            'mealOptionIds': self.get_meal_option_ids(),
        }
