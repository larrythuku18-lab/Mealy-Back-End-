"""
Standardized error response helpers for consistent API error format
across all route handlers.
"""
from flask import jsonify


def error_response(message, status_code, details=None):
    """
    Create a standardized error response.
    
    Args:
        message: Human-readable error message
        status_code: HTTP status code
        details: Optional additional error details
    
    Returns:
        Tuple of (jsonify response, status code)
    """
    body = {'error': message}
    if details:
        body['details'] = details
    return jsonify(body), status_code


def bad_request(message='Bad request'):
    return error_response(message, 400)


def unauthorized(message='Unauthorized'):
    return error_response(message, 401)


def forbidden(message='Forbidden'):
    return error_response(message, 403)


def not_found(message='Resource not found'):
    return error_response(message, 404)


def conflict(message='Resource already exists'):
    return error_response(message, 409)


def server_error(message='Internal server error'):
    return error_response(message, 500)
