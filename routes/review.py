from flask import Blueprint, request, jsonify, g

from config import db
from models import Review, MealOption
from routes.auth import auth_required

review_bp = Blueprint('review', __name__)


@review_bp.route('/', methods=['POST'])
@auth_required
def create_review():
    data = request.get_json()
    meal_option_id = data.get('meal_option_id')
    rating = data.get('rating')
    comment = data.get('comment')

    if not meal_option_id or rating is None:
        return jsonify({'error': 'meal_option_id and rating are required'}), 400

    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be an integer between 1 and 5'}), 400

    meal_option = db.session.get(MealOption, meal_option_id)
    if not meal_option:
        return jsonify({'error': 'Meal option not found'}), 404

    # Check if user already reviewed this meal option
    existing = Review.query.filter_by(
        user_id=g.current_user.id,
        meal_option_id=meal_option_id
    ).first()
    if existing:
        return jsonify({'error': 'You have already reviewed this meal option'}), 409

    review = Review(
        user_id=g.current_user.id,
        meal_option_id=meal_option_id,
        rating=rating,
        comment=comment,
    )
    db.session.add(review)
    db.session.commit()

    return jsonify({
        'message': 'Review created successfully',
        'review': review.to_dict()
    }), 201


@review_bp.route('/<int:meal_option_id>', methods=['GET'])
def get_reviews(meal_option_id):
    """Get all reviews for a specific meal option."""
    reviews = Review.query.filter_by(meal_option_id=meal_option_id).all()
    return jsonify({
        'reviews': [r.to_dict() for r in reviews]
    }), 200
