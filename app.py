import os
import click
from flask import Flask, jsonify, g, request
from flask_cors import CORS
from datetime import datetime, timezone
from config import db, Config

basedir = os.path.abspath(os.path.dirname(__file__))


def create_app(config_name=None):
    """Application factory pattern."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)

    from config import config_by_name
    app.config.from_object(config_by_name.get(config_name, Config))

    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/*": {"origins": app.config.get('CORS_ORIGINS', '*')}})

    # Initialize middleware
    from middleware import init_middleware
    init_middleware(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.menu import menu_bp
    from routes.order import order_bp
    from routes.review import review_bp
    from routes.royalty import royalty_bp
    from routes.category import category_bp
    from routes.payment import payment_bp
    from routes.notification import notification_bp
    from routes.sales import sales_bp

    # Auth, menu, and order blueprints are mounted under both the
    # documented /api/* prefixes and the bare paths (/auth, /menu,
    # /orders) that the deployed Mealy frontend calls.
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(auth_bp, url_prefix='/auth', name='auth_frontend')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(menu_bp, url_prefix='/api/menus')
    app.register_blueprint(menu_bp, url_prefix='/menu', name='menu_frontend')
    app.register_blueprint(order_bp, url_prefix='/api/orders')
    app.register_blueprint(order_bp, url_prefix='/orders', name='order_frontend')
    app.register_blueprint(review_bp, url_prefix='/api/reviews')
    app.register_blueprint(royalty_bp, url_prefix='/api/royalties')
    app.register_blueprint(category_bp, url_prefix='/api/categories')
    app.register_blueprint(payment_bp, url_prefix='/api/payments')
    app.register_blueprint(notification_bp, url_prefix='/api/notifications')
    app.register_blueprint(sales_bp, url_prefix='/api/sales')
    # Health check routes
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            'message': 'Mealy Backend API v2.0',
            'status': 'running',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'UP',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200

    # TEMPORARY one-off maintenance route: clears the placehold.co image
    # URLs backfilled earlier — they bake their ?text= label into the
    # image, which duplicates the dish name once the frontend also shows
    # it as a heading (the new dish slideshow). Same gate/pattern as the
    # earlier maintenance routes; remove after use.
    @app.route('/api/_maintenance/clear-images', methods=['POST'])
    def maintenance_clear_images():
        import hmac
        expected = os.getenv('ADMIN_RESET_TOKEN')
        if not expected:
            return jsonify({'error': 'Not found'}), 404
        provided = request.headers.get('X-Reset-Token', '')
        if not hmac.compare_digest(provided, expected):
            return jsonify({'error': 'Not found'}), 404

        from models import MealOption
        updated = 0
        for meal_option in MealOption.query.filter(
            MealOption.image.like('https://placehold.co/%')
        ).all():
            meal_option.image = None
            updated += 1
        db.session.commit()
        return jsonify({'message': f'Cleared {updated} meal option image(s)'}), 200

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400

    # Create tables
    with app.app_context():
        db.create_all()

    # CLI commands
    @app.cli.command('seed')
    def seed_command():
        """Seed the database with initial data."""
        from seed import seed_database
        seed_database()
        click.echo('Database seeded!')

    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
