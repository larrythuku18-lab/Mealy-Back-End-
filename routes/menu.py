from datetime import date
from flask import Blueprint, request, jsonify

from config import db
from models import MealOption, DailyMenu, Category
from routes.auth import auth_required
from errors import bad_request, not_found
from validators import get_json_or_400, validate_required_fields

menu_bp = Blueprint('menu', __name__)


# --- Meal Options CRUD (Admin) ---

@menu_bp.route('/', methods=['GET'])
def list_meal_options():
    """List all meal options. If ?available=true, only show available ones."""
    meal_options = MealOption.query.all()
    return jsonify({
        'mealOptions': [mo.to_dict() for mo in meal_options]
    }), 200


@menu_bp.route('/', methods=['POST'])
@auth_required
def create_meal_option():
    data, err = get_json_or_400()
    if err:
        return err

    ok, field_err = validate_required_fields(data, ['name', 'price'])
    if not ok:
        return field_err

    name = data.get('name')
    description = data.get('description')
    price = data.get('price')

    meal_option = MealOption(
        name=name,
        description=description,
        price=float(price),
        category=data.get('category'),
        image=data.get('image'),
        caterer_id=data.get('catererId'),
    )
    db.session.add(meal_option)
    db.session.commit()

    return jsonify({
        'message': 'Meal option created successfully',
        'mealOption': meal_option.to_dict()
    }), 201


@menu_bp.route('/<int:meal_option_id>', methods=['GET'])
def get_meal_option(meal_option_id):
    meal_option = db.session.get(MealOption, meal_option_id)
    if not meal_option:
        return not_found('Meal option not found')
    return jsonify({'mealOption': meal_option.to_dict()}), 200


@menu_bp.route('/<int:meal_option_id>', methods=['PUT'])
@auth_required
def update_meal_option(meal_option_id):
    data, err = get_json_or_400()
    if err:
        return err
    meal_option = db.session.get(MealOption, meal_option_id)
    if not meal_option:
        return not_found('Meal option not found')

    if 'name' in data:
        meal_option.name = data['name']
    if 'description' in data:
        meal_option.description = data['description']
    if 'price' in data:
        meal_option.price = float(data['price'])
    if 'category' in data:
        meal_option.category = data['category']
    if 'image' in data:
        meal_option.image = data['image']
    if 'catererId' in data:
        meal_option.caterer_id = data['catererId']

    db.session.commit()

    return jsonify({
        'message': 'Meal option updated successfully',
        'mealOption': meal_option.to_dict()
    }), 200


@menu_bp.route('/<int:meal_option_id>', methods=['DELETE'])
@auth_required
def delete_meal_option(meal_option_id):
    meal_option = db.session.get(MealOption, meal_option_id)
    if not meal_option:
        return not_found('Meal option not found')

    db.session.delete(meal_option)
    db.session.commit()

    return jsonify({'message': 'Meal option deleted successfully'}), 200


# --- Today's Menu ---

@menu_bp.route('/today', methods=['GET'])
def get_todays_menu():
    """Get today's published menu with meal option IDs."""
    today = date.today()
    daily_menu = DailyMenu.query.filter_by(date=today).first()

    if not daily_menu:
        return jsonify({
            'mealOptionIds': [],
            'isPublished': False,
        }), 200

    return jsonify(daily_menu.to_dict()), 200


@menu_bp.route('/publish', methods=['POST'])
@auth_required
def publish_todays_menu():
    """Publish today's menu with selected meal option IDs."""
    data, err = get_json_or_400()
    if err:
        return err
    meal_option_ids = data.get('mealOptionIds', [])

    today = date.today()
    daily_menu = DailyMenu.query.filter_by(date=today).first()

    if not daily_menu:
        daily_menu = DailyMenu(date=today)
        db.session.add(daily_menu)

    daily_menu.set_meal_option_ids(meal_option_ids)
    daily_menu.is_published = True

    db.session.commit()

    return jsonify({
        'message': 'Menu published successfully',
        **daily_menu.to_dict()
    }), 200
