import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import Blueprint, request, jsonify, g, current_app

from config import db
from models import User
from errors import bad_request, unauthorized, conflict
from validators import get_json_or_400, validate_email


auth_bp = Blueprint('auth', __name__)


# JWT AUTHENTICATION

def auth_required(f):
    """
    Protect a route and require a valid JWT token.
    """

    @wraps(f)
    def decorated(*args, **kwargs):

        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return unauthorized('Authorization header required')


        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return unauthorized(
                'Authorization header must be: Bearer <token>'
            )

        token = parts[1]

        try:
            data = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )

            user_id = data.get('user_id')

            if not user_id:
                return unauthorized('Invalid token')

            user = db.session.get(User, user_id)

            if not user:
                return unauthorized('User not found')

            g.current_user = user

        except jwt.ExpiredSignatureError:
            return unauthorized('Token has expired')

        except jwt.InvalidTokenError:
            return unauthorized('Invalid token')

        return f(*args, **kwargs)

    return decorated


def generate_token(user):
    """
    Generate a JWT token for a user.
    """

    token = jwt.encode(
        {
            'user_id': user.id,
            'role': user.role,
            'exp': datetime.now(timezone.utc) + timedelta(
                seconds=current_app.config.get(
                    'JWT_ACCESS_TOKEN_EXPIRES',
                    3600
                )
            )
        },
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )

    return token


# ROLE AUTHORIZATION

def role_required(*allowed_roles):
    """
    Restrict a route to specific user roles.

    Example:

        @role_required('admin')
        def admin_route():
            ...
    """

    def decorator(f):

        @wraps(f)
        @auth_required
        def decorated(*args, **kwargs):

            if g.current_user.role not in allowed_roles:
                return jsonify({
                    'error': 'You do not have permission to access this resource'
                }), 403

            return f(*args, **kwargs)

        return decorated

    return decorator


# REGISTER

@auth_bp.route('/register', methods=['POST'])
def register():

    data, err = get_json_or_400()

    if err:
        return err

    name = data.get('name') or data.get('full_name') or data.get('fullName')

    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone')
    address = data.get('address')

    if not name or not email or not password:
        return bad_request(
            'Name, email, and password are required'
        )

    ok, email_err = validate_email(email)

    if not ok:
        return email_err

    email = email.strip().lower()

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return conflict('Email already exists')

    if len(password) < 6:
        return bad_request(
            'Password must be at least 6 characters'
        )

    password_hash = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

    user = User(
        name=name,
        email=email,
        password_hash=password_hash,
        phone=phone,
        role='user',
        address=address
    )

    db.session.add(user)
    db.session.commit()

    token = generate_token(user)

    return jsonify({
        'message': 'User registered successfully',
        'token': token,
        'user': user.to_dict()
    }), 201
    
