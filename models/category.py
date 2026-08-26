from config import db


class Category(db.Model):
    """Meal category (Breakfast, Lunch, Dinner, Snacks, Drinks)."""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }
