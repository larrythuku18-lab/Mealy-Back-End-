"""
Application middleware for request logging, CORS preflight,
and common before/after request hooks.
"""
import logging
from flask import g, request
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def init_middleware(app):
    """Register before/after request middleware on the Flask app."""

    @app.before_request
    def before_request():
        g.request_start_time = datetime.now(timezone.utc)
        # Handle CORS preflight
        if request.method == 'OPTIONS':
            return '', 204

    @app.after_request
    def after_request(response):
        # Add request timing header
        if hasattr(g, 'request_start_time'):
            elapsed = (datetime.now(timezone.utc) - g.request_start_time).total_seconds() * 1000
            response.headers['X-Response-Time'] = f'{elapsed:.1f}ms'

        # Standard CORS headers
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Max-Age'] = '3600'

        # Log non-health-check requests
        if request.path not in ('/', '/health'):
            logger.info(
                '%s %s %s %s %.1fms',
                request.method,
                request.path,
                response.status_code,
                request.remote_addr,
                elapsed if hasattr(g, 'request_start_time') else 0,
            )

        return response
