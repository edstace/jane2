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

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)

def create_app(config=None):
    """Application factory function"""
    app = Flask(__name__, static_url_path='/static')
    
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
    
    # Register error handlers
    register_error_handlers(app)
    
    return app

def register_error_handlers(app):
    """Register error handlers"""
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.error(f"404 error: {error}")
        from flask import jsonify
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(429)
    def ratelimit_handler(error):
        app.logger.warning(f"Rate limit exceeded: {error}")
        from flask import jsonify, request
        return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"500 error: {error}")
        from flask import jsonify
        return jsonify({'error': 'Internal server error'}), 500