import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import Blueprint, request, jsonify, g, current_app

from config import db
from models import User

auth_bp = Blueprint('auth', __name__)


def auth_required(f):
    """Decorator to require a valid JWT token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization header required'}), 401

        try:
            token = auth_header.split(' ')[1]
            data = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            user = db.session.get(User, data['user_id'])
            if not user:
                return jsonify({'error': 'User not found'}), 401
            g.current_user = user
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except (jwt.InvalidTokenError, IndexError):
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)
    return decorated


def generate_token(user):
    """Generate a JWT token for the given user."""
    return jwt.encode(
        {
            'user_id': user.id,
            'exp': datetime.now(timezone.utc) + timedelta(
                seconds=current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 3600)
            )
        },
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Frontend sends 'fullName', we store as 'name'
    name = data.get('name') or data.get('fullName')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 409

    password_hash = bcrypt.hashpw(
        password.encode('utf-8'), bcrypt.gensalt()
    ).decode('utf-8')

    user = User(
        name=name,
        email=email,
        password_hash=password_hash,
        phone=data.get('phone'),
        role=data.get('role', 'user'),
        address=data.get('address'),
    )
    db.session.add(user)
    db.session.commit()

    token = generate_token(user)

    return jsonify({
        'message': 'User registered successfully',
        'token': token,
        'user': user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Frontend sends email for login
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = generate_token(user)

    return jsonify({
        'message': 'Logged in successfully',
        'token': token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@auth_required
def logout():
    return jsonify({'message': 'Logged out successfully'}), 200


@auth_bp.route('/me', methods=['GET'])
@auth_required
def me():
    return jsonify({'user': g.current_user.to_dict()}), 200
