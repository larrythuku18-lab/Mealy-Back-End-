"""
Vercel serverless function entry point.
Imports the Flask application from the root app.py.
"""
import sys
import os

# Add the parent directory to sys.path so we can import app.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel expects a WSGI app named 'app'
