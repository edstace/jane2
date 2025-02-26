from flask import jsonify, current_app, g
from app.exceptions import BaseError, APIError, DatabaseError, ValidationError
from app.middleware import get_request_id
import traceback

def register_error_handlers(app):
    """Register error handlers for the application"""
    
    def get_safe_request_id():
        """Safely get request ID if available"""
        try:
            return get_request_id()
        except Exception:
            return 'NO_REQUEST_ID'
    
    @app.errorhandler(BaseError)
    def handle_base_error(error):
        """Handle all custom exceptions"""
        request_id = get_safe_request_id()
        current_app.logger.error(f'Request {request_id} failed with {error.__class__.__name__}: {str(error)}')
        response = {
            'error': {
                'code': error.code,
                'message': error.message,
                'request_id': request_id
            }
        }
        return jsonify(response), error.status_code

    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 Not Found errors"""
        request_id = get_safe_request_id()
        current_app.logger.warning(f'Request {request_id}: Resource not found')
        response = {
            'error': {
                'code': 'NOT_FOUND',
                'message': 'The requested resource was not found',
                'request_id': request_id
            }
        }
        return jsonify(response), 404

    @app.errorhandler(429)
    def handle_rate_limit(error):
        """Handle rate limit exceeded errors"""
        request_id = get_safe_request_id()
        current_app.logger.warning(f'Request {request_id}: Rate limit exceeded')
        response = {
            'error': {
                'code': 'RATE_LIMIT_EXCEEDED',
                'message': 'Too many requests. Please try again later.',
                'request_id': request_id
            }
        }
        return jsonify(response), 429

    @app.errorhandler(500)
    def handle_server_error(error):
        """Handle internal server errors"""
        request_id = get_safe_request_id()
        current_app.logger.error(f'Request {request_id} failed with unexpected error: {str(error)}')
        current_app.logger.error(traceback.format_exc())
        response = {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An unexpected error occurred',
                'request_id': request_id
            }
        }
        if current_app.debug:
            response['error']['debug_info'] = {
                'traceback': traceback.format_exc(),
                'error_type': error.__class__.__name__
            }
        return jsonify(response), 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle any unhandled exceptions"""
        request_id = get_safe_request_id()
        current_app.logger.error(f'Request {request_id} failed with unhandled error: {str(error)}')
        current_app.logger.error(traceback.format_exc())
        response = {
            'error': {
                'code': 'UNEXPECTED_ERROR',
                'message': 'An unexpected error occurred',
                'request_id': request_id
            }
        }
        if current_app.debug:
            response['error']['debug_info'] = {
                'traceback': traceback.format_exc(),
                'error_type': error.__class__.__name__
            }
        return jsonify(response), 500
