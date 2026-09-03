import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()


class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///mealy.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Managed Postgres (Neon, etc.) closes idle connections; on a warm-but-
    # idle serverless instance SQLAlchemy would otherwise hand out a pooled
    # connection the DB has already dropped ("SSL connection has been
    # closed unexpectedly"). pre_ping tests each connection before use and
    # transparently reconnects; recycle proactively retires connections
    # before they're likely to have gone stale.
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
    }
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))

    # M-Pesa configuration
    MPESA_CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY')
    MPESA_CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET')
    MPESA_SHORTCODE = os.getenv('MPESA_SHORTCODE')
    MPESA_PASSKEY = os.getenv('MPESA_PASSKEY')
    MPESA_CALLBACK_URL = os.getenv('MPESA_CALLBACK_URL')
    MPESA_ENVIRONMENT = os.getenv('MPESA_ENVIRONMENT', 'sandbox')

    
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
