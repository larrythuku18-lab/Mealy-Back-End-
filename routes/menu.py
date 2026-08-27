from datetime import date
from flask import Blueprint, request, jsonify, g

from config import db
from models import MealOption, DailyMenu, Category, Notification, User
from routes.auth import auth_required,role_required
from errors import bad_request, not_found
from validators import get_json_or_400, validate_required_fields

menu_bp = Blueprint('menu', __name__)


# --- Meal Options CRUD (Admin) ---

@menu_bp.route('/', methods=['GET'])
@auth_required
def list_meal_options():
    """List meal options belonging to the current user's caterer."""

    caterer_id = g.current_user.caterer_id

    if not caterer_id:
        return bad_request('User is not associated with a caterer')

    meal_options = MealOption.query.filter_by(
        caterer_id=caterer_id
    ).all()

    return jsonify({
        'mealOptions': [mo.to_dict() for mo in meal_options]
    }), 200



@menu_bp.route('/', methods=['POST'])
@role_required('admin')
def create_meal_option():
    data, err = get_json_or_400()
    if err:
        return err

    # Make sure the admin belongs to a caterer
    if not g.current_user.caterer_id:
        return bad_request(
            'Admin is not associated with a caterer'
        )

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
        caterer_id=g.current_user.caterer_id,
    )

    db.session.add(meal_option)
    db.session.commit()

    return jsonify({
        'message': 'Meal option created successfully',
        'mealOption': meal_option.to_dict()
    }), 201



@menu_bp.route('/<int:meal_option_id>', methods=['GET'])
@auth_required
def get_meal_option(meal_option_id):
    meal_option = db.session.get(MealOption, meal_option_id)

    if not meal_option:
        return not_found('Meal option not found')

    if str(meal_option.caterer_id) != str(g.current_user.caterer_id):
        return not_found('Meal option not found')

    return jsonify({
        'mealOption': meal_option.to_dict()
    }), 200


@menu_bp.route('/<int:meal_option_id>', methods=['PUT'])
@role_required('admin')
def update_meal_option(meal_option_id):
    data, err = get_json_or_400()
    if err:
        return err
    meal_option = db.session.get(MealOption, meal_option_id)
    if not meal_option:
        return not_found('Meal option not found')
    if str(meal_option.caterer_id) != str(g.current_user.caterer_id):
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

    db.session.commit()

    return jsonify({
        'message': 'Meal option updated successfully',
        'mealOption': meal_option.to_dict()
    }), 200


@menu_bp.route('/<int:meal_option_id>', methods=['DELETE'])
@role_required('admin')
def delete_meal_option(meal_option_id):
    meal_option = db.session.get(MealOption, meal_option_id)
    if not meal_option:
        return not_found('Meal option not found')
    if str(meal_option.caterer_id) != str(g.current_user.caterer_id):
        return not_found('Meal option not found')

    db.session.delete(meal_option)
    db.session.commit()

    return jsonify({'message': 'Meal option deleted successfully'}), 200


# --- Today's Menu ---

@menu_bp.route('/today', methods=['GET'])
@auth_required
def get_todays_menu():
    """Get today's menu for the current user's caterer."""

    caterer_id = g.current_user.caterer_id

    if not caterer_id:
        return bad_request('User is not associated with a caterer')

    today = date.today()

    daily_menu = DailyMenu.query.filter_by(
        caterer_id=caterer_id,
        date=today
    ).first()

    if not daily_menu:
        return jsonify({
            'mealOptionIds': [],
            'isPublished': False,
        }), 200

    return jsonify(daily_menu.to_dict()), 200

@menu_bp.route('/date/<menu_date>', methods=['GET'])
@auth_required
def get_menu_by_date(menu_date):
    """Get the published menu for a specific date."""

    caterer_id = g.current_user.caterer_id

    if not caterer_id:
        return bad_request('User is not associated with a caterer')

    try:
        requested_date = date.fromisoformat(menu_date)
    except ValueError:
        return bad_request(
            'Invalid date format. Use YYYY-MM-DD'
        )

    daily_menu = DailyMenu.query.filter_by(
        caterer_id=caterer_id,
        date=requested_date
    ).first()

    if not daily_menu:
        return jsonify({
            'date': menu_date,
            'mealOptionIds': [],
            'isPublished': False,
        }), 200

    return jsonify(daily_menu.to_dict()), 200




@menu_bp.route('/publish', methods=['POST'])
@role_required('admin')
def publish_menu():
    """Publish a menu for a specific date."""

    data, err = get_json_or_400()
    if err:
        return err

    if not g.current_user.caterer_id:
        return bad_request(
            'Admin is not associated with a caterer'
        )

    menu_date = data.get('date')
    meal_option_ids = data.get('mealOptionIds', [])

    if not menu_date:
        return bad_request('date is required')

    if not meal_option_ids:
        return bad_request('mealOptionIds are required')

    # Convert date from string to Python date
    try:
        menu_date = date.fromisoformat(menu_date)
    except ValueError:
        return bad_request(
            'Invalid date format. Use YYYY-MM-DD'
        )

    # Check that all meal options exist
    for meal_id in meal_option_ids:
        meal_option = db.session.get(MealOption, meal_id)

        if not meal_option:
            return not_found(
                f'Meal option {meal_id} not found'
            )

        if str(meal_option.caterer_id) != str(g.current_user.caterer_id):
            return not_found(
                f'Meal option {meal_id} not found'
            )

    # Find existing menu for this date
    daily_menu = DailyMenu.query.filter_by(
       caterer_id=g.current_user.caterer_id,
       date=menu_date
    ).first()

    # Create menu if it doesn't exist
    if not daily_menu:
        daily_menu = DailyMenu(
            caterer_id=g.current_user.caterer_id,
            date=menu_date
        )
        db.session.add(daily_menu)

    # Set meal options and publish
    daily_menu.set_meal_option_ids(meal_option_ids)
    daily_menu.is_published = True

    # Notify all customers
    customers = User.query.filter_by(
        role='customer',
        caterer_id=g.current_user.caterer_id
    ).all()

    for customer in customers:
        notification = Notification(
            user_id=customer.id,
            title="Menu is Ready!",
            message=f"The menu for {menu_date.isoformat()} has been published."
        )
        db.session.add(notification)

    db.session.commit()

    return jsonify({
        'message': 'Menu published successfully',
        'menu': daily_menu.to_dict()
    }), 200