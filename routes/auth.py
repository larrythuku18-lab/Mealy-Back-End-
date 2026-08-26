import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import Blueprint, request, jsonify, g, current_app

from config import db
from models import User
from errors import bad_request, unauthorized, conflict, not_found
from validators import get_json_or_400, validate_required_fields, validate_email

auth_bp = Blueprint('auth', __name__)


def auth_required(f):
    """Decorator to require a valid JWT token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return unauthorized('Authorization header required')

        try:
            token = auth_header.split(' ')[1]
            data = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            user = db.session.get(User, data['user_id'])
            if not user:
                return unauthorized('User not found')
            g.current_user = user
        except jwt.ExpiredSignatureError:
            return unauthorized('Token has expired')
        except (jwt.InvalidTokenError, IndexError):
            return unauthorized('Invalid token')

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
    data, err = get_json_or_400()
    if err:
        return err

    # Frontend sends 'fullName', we store as 'name'
    name = data.get('name') or data.get('fullName')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return bad_request('Name, email, and password are required')

    ok, email_err = validate_email(email)
    if not ok:
        return email_err

    if User.query.filter_by(email=email).first():
        return conflict('Email already exists')

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
    data, err = get_json_or_400()
    if err:
        return err

    # Frontend sends email for login
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return bad_request('Email and password are required')

    user = User.query.filter_by(email=email).first()
    if not user:
        return unauthorized('Invalid credentials')

    if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return unauthorized('Invalid credentials')

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
