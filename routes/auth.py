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

        # Expected format:
        # Authorization: Bearer <token>

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

            # Store authenticated user for the request
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


