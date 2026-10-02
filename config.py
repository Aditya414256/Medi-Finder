import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'medifind-dev-secure-key-2026-default')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    PORT = int(os.getenv('PORT', 5000))

    # Database resolution
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        mysql_user = os.getenv('MYSQL_USER')
        mysql_pwd = os.getenv('MYSQL_PASSWORD')
        mysql_host = os.getenv('MYSQL_HOST', 'localhost')
        mysql_port = os.getenv('MYSQL_PORT', '3306')
        mysql_db = os.getenv('MYSQL_DATABASE')
        if mysql_user and mysql_db:
            DATABASE_URL = f"mysql+pymysql://{mysql_user}:{mysql_pwd}@{mysql_host}:{mysql_port}/{mysql_db}"
        else:
            db_path = BASE_DIR / 'medifind.db'
            DATABASE_URL = f"sqlite:///{db_path}"

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
    } if 'mysql' in DATABASE_URL else {}

    # File uploads
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', str(BASE_DIR / 'uploads'))
    if not os.path.isabs(UPLOAD_FOLDER):
        UPLOAD_FOLDER = str(BASE_DIR / UPLOAD_FOLDER)
    
    # Subdirectories for secure uploads
    PRESCRIPTIONS_DIR = os.path.join(UPLOAD_FOLDER, 'prescriptions')
    VERIFICATION_DOCS_DIR = os.path.join(UPLOAD_FOLDER, 'verification_docs')

    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 10 * 1024 * 1024)) # 10MB
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

    # Security & Sessions
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 60 * 60 * 24 * 14  # 14 days


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    UPLOAD_FOLDER = str(BASE_DIR / 'tests' / 'test_uploads')
    PRESCRIPTIONS_DIR = os.path.join(UPLOAD_FOLDER, 'prescriptions')
    VERIFICATION_DOCS_DIR = os.path.join(UPLOAD_FOLDER, 'verification_docs')


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
