import os
import click
from flask import Flask, jsonify, g
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

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(menu_bp, url_prefix='/api/menus')
    app.register_blueprint(order_bp, url_prefix='/api/orders')
    app.register_blueprint(review_bp, url_prefix='/api/reviews')
    app.register_blueprint(royalty_bp, url_prefix='/api/royalties')
    app.register_blueprint(category_bp, url_prefix='/api/categories')
    app.register_blueprint(payment_bp, url_prefix='/api/payments')

    
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
