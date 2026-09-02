"""
Vercel serverless function entry point.
Imports the Flask application from the root app.py.
"""
import sys
import os
from datetime import datetime, timezone

# Add the parent directory to sys.path so we can import app.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from flask import jsonify


# Vercel health check route (accessible at /api/health)
@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({
        'status': 'UP',
        'service': 'mealy-backend',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'environment': os.getenv('FLASK_ENV', 'development')
    }), 200


# Vercel expects a WSGI app named 'app'
