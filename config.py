"""
Configuration file for SmartEdu AI
Contains environment-specific settings and configuration variables
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Basic Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:password@localhost/smartedu'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 120,
        'pool_pre_ping': True
    }
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Face Recognition Configuration
    FACE_RECOGNITION_TOLERANCE = 0.6
    FACE_RECOGNITION_MODEL = 'hog'  # or 'cnn' for more accurate but slower
    FACE_ENCODING_DETECTIONS = 1  # Number of face detections per image
    
    # Machine Learning Configuration
    MODEL_RETRAINING_INTERVAL = timedelta(days=7)  # Retrain models weekly
    PREDICTION_CONFIDENCE_THRESHOLD = 0.8
    RISK_ALERT_THRESHOLD = 0.7
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Email Configuration (for notifications)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@smartedu.ai'
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'smartedu.log'
    
    # Security Configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Cache Configuration
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"
    
    # API Configuration
    API_VERSION = 'v1'
    API_PREFIX = f'/api/{API_VERSION}'
    
    # Pagination
    POSTS_PER_PAGE = 20
    MAX_SEARCH_RESULTS = 50
    
    # Performance Monitoring
    ENABLE_PERFORMANCE_MONITORING = True
    SLOW_QUERY_THRESHOLD = 1000  # milliseconds
    
    # Backup Configuration
    BACKUP_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
    AUTO_BACKUP_ENABLED = True
    BACKUP_RETENTION_DAYS = 30
    
    # Feature Flags
    ENABLE_FACE_RECOGNITION = True
    ENABLE_ML_PREDICTIONS = True
    ENABLE_EMAIL_NOTIFICATIONS = True
    ENABLE_REAL_TIME_ALERTS = True
    
    @staticmethod
    def init_app(app):
        """Initialize application with this configuration"""
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    
    DEBUG = True
    TESTING = False
    
    # Use SQLite for development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'smartedu_dev.db')
    
    # Disable security features for development
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False
    
    # Enable debug toolbar
    ENABLE_DEBUG_TOOLBAR = True
    
    # Log all SQL queries
    SQLALCHEMY_RECORD_QUERIES = True
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Import and initialize debug toolbar if available
        try:
            from flask_debugtoolbar import DebugToolbarExtension
            DebugToolbarExtension(app)
        except ImportError:
            pass

class TestingConfig(Config):
    """Testing configuration"""
    
    TESTING = True
    DEBUG = True
    
    # Use in-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Disable email sending
    MAIL_SUPPRESS_SEND = True
    
    # Faster password hashing for testing
    LOGIN_DISABLED = False
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)

class ProductionConfig(Config):
    """Production configuration"""
    
    DEBUG = False
    TESTING = False
    
    # Production database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://user:password@localhost/smartedu_prod'
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Enable all security features
    WTF_CSRF_ENABLED = True
    
    # Production logging
    LOG_LEVEL = 'WARNING'
    
    # Performance optimizations
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'pool_timeout': 30
    }
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Setup production logging
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            
            file_handler = RotatingFileHandler(
                'logs/smartedu.log', 
                maxBytes=10240000, 
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('SmartEdu AI startup')

class StagingConfig(Config):
    """Staging configuration (similar to production but with debug features)"""
    
    DEBUG = True
    TESTING = False
    
    # Staging database
    SQLALCHEMY_DATABASE_URI = os.environ.get('STAGING_DATABASE_URL') or \
        'mysql+pymysql://user:password@localhost/smartedu_staging'
    
    # Enable some debug features
    SQLALCHEMY_RECORD_QUERIES = True
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'staging': StagingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment variable"""
    return config[os.environ.get('FLASK_ENV', 'default')]

# Environment-specific helper functions
def is_development():
    """Check if running in development environment"""
    return os.environ.get('FLASK_ENV') == 'development'

def is_production():
    """Check if running in production environment"""
    return os.environ.get('FLASK_ENV') == 'production'

def is_testing():
    """Check if running in testing environment"""
    return os.environ.get('FLASK_ENV') == 'testing'
