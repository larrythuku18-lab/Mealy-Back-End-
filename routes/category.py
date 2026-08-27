from flask import Blueprint, request, jsonify

from config import db
from models import Category
from routes.auth import auth_required, role_required
category_bp = Blueprint('category', __name__)


@category_bp.route('/', methods=['GET'])
def list_categories():
    """List all meal categories."""
    categories = Category.query.all()
    return jsonify({
        'categories': [c.to_dict() for c in categories]
    }), 200


@category_bp.route('/', methods=['POST'])
@role_required('admin')
def create_category():
    """Create a new category (admin only)."""
    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({'error': 'Category name is required'}), 400

    if Category.query.filter_by(name=name).first():
        return jsonify({'error': 'Category already exists'}), 409

    category = Category(name=name)
    db.session.add(category)
    db.session.commit()

    return jsonify({
        'message': 'Category created successfully',
        'category': category.to_dict()
    }), 201
