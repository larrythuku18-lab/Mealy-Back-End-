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

    # TEMPORARY one-off maintenance route: the production database has a
    # stale schema (caterer_id was INTEGER under an older version of the
    # models; the app now treats it as a string), and db.create_all() only
    # creates missing tables, never alters existing ones. This re-runs the
    # same drop/recreate/reseed the `flask seed` CLI command does, since
    # that CLI isn't reachable on Vercel's serverless deployment. Requires
    # ADMIN_RESET_TOKEN to be set; fails closed (404) if it isn't, and
    # remove this route + the env var once the reset has been run.
    @app.route('/api/_maintenance/reset-db', methods=['POST'])
    def maintenance_reset_db():
        import hmac
        expected = os.getenv('ADMIN_RESET_TOKEN')
        if not expected:
            return jsonify({'error': 'Not found'}), 404
        provided = request.headers.get('X-Reset-Token', '')
        if not hmac.compare_digest(provided, expected):
            return jsonify({'error': 'Not found'}), 404

        from seed import seed_database
        seed_database()
        return jsonify({'message': 'Database reset and reseeded'}), 200

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
