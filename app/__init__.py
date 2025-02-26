from flask import Flask
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import logging
from logging.handlers import RotatingFileHandler
from app.middleware import RequestIDMiddleware
from app.handlers import register_error_handlers

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)

def create_app(config=None):
    """Application factory function"""
    # Setting template_folder and static_folder for compatibility with different environments
    # This allows templates and static files to be found whether they're in the app/ directory
    # or in the root directory (for backward compatibility)
    app = Flask(__name__, 
               static_url_path='/static',
               static_folder='static',
               template_folder='templates')
    
    # Load configuration
    if config is None:
        # Load configuration from module
        from app.config.config import Config
        app.config.from_object(Config)
    else:
        # Load configuration from parameter
        app.config.from_object(config)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    limiter.init_app(app)
    
    # Initialize Talisman in production
    if app.config['ENV'] == 'production':
        Talisman(app, content_security_policy={
            'default-src': "'self'",
            'script-src': ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net"],
            'style-src': ["'self'", "'unsafe-inline'", "fonts.googleapis.com", "cdn.jsdelivr.net"],
            'font-src': ["'self'", "fonts.gstatic.com", "cdn.jsdelivr.net"],
            'img-src': ["'self'", "data:", "https:"],
        })
    
    # Configure logging
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler = RotatingFileHandler(
        'logs/jane.log', 
        maxBytes=10240, 
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    
    # Register blueprints
    from app.routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from app.routes.chat import chat_bp as chat_blueprint
    app.register_blueprint(chat_blueprint)
    
    from app.routes.sms import sms_bp as sms_blueprint
    app.register_blueprint(sms_blueprint, url_prefix='/sms')
    
    # Add request ID middleware
    app.wsgi_app = RequestIDMiddleware(app.wsgi_app)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app
