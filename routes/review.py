from flask import Blueprint, request, jsonify, g

from config import db
from models import Review, MealOption
from routes.auth import auth_required
from errors import bad_request, not_found, conflict
from validators import get_json_or_400, validate_required_fields, validate_rating

review_bp = Blueprint('review', __name__)


@review_bp.route('/', methods=['POST'])
@auth_required
def create_review():
    data, err = get_json_or_400()
    if err:
        return err

    ok, field_err = validate_required_fields(data, ['meal_option_id', 'rating'])
    if not ok:
        return field_err

    meal_option_id = data.get('meal_option_id')
    rating = data.get('rating')
    comment = data.get('comment')

    ok, rating_err = validate_rating(rating)
    if not ok:
        return rating_err

    meal_option = db.session.get(MealOption, meal_option_id)
    if not meal_option:
        return not_found('Meal option not found')

    # Check if user already reviewed this meal option
    existing = Review.query.filter_by(
        user_id=g.current_user.id,
        meal_option_id=meal_option_id
    ).first()
    if existing:
        return conflict('You have already reviewed this meal option')

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
