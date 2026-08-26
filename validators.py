"""
Input validation utilities for consistent request validation
across all route handlers.
"""
from flask import request, jsonify


def get_json_or_400():
    """Parse JSON body or return 400 if invalid."""
    data = request.get_json(silent=True)
    if data is None:
        return None, (jsonify({'error': 'Invalid JSON body'}), 400)
    return data, None


def validate_required_fields(data, required_fields):
    """
    Check that all required fields are present and non-empty.
    Returns (True, None) on success or (False, error_response) on failure.
    """
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return False, (
            jsonify({'error': f'Missing required fields: {", ".join(missing)}'}),
            400
        )
    return True, None


def validate_email(email):
    """Basic email format validation."""
    if not email or '@' not in email or '.' not in email.split('@')[-1]:
        return False, (jsonify({'error': 'Invalid email format'}), 400)
    return True, None


def validate_rating(rating):
    """Validate rating is an integer between 1 and 5."""
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return False, (jsonify({'error': 'Rating must be an integer between 1 and 5'}), 400)
    return True, None


def validate_price(price):
    """Validate price is a positive number."""
    try:
        price = float(price)
        if price <= 0:
            raise ValueError
        return True, price
    except (TypeError, ValueError):
        return False, (jsonify({'error': 'Price must be a positive number'}), 400)


def validate_order_status(status):
    """Validate order status is one of the allowed values."""
    valid = ['confirmed', 'preparing', 'in_transit', 'delivered']
    if status not in valid:
        return False, (
            jsonify({'error': f'Status must be one of: {", ".join(valid)}'}),
            400
        )
    return True, None
