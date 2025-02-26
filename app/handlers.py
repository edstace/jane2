from flask import jsonify, current_app, g, request
from app.exceptions import BaseError, APIError, DatabaseError, ValidationError
from app.middleware import get_request_id
import traceback
import sentry_sdk

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
        # Log error
        current_app.logger.error(f'Request {request_id} failed with {error.__class__.__name__}: {str(error)}')
        
        # Add extra context to Sentry
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("error_code", error.code)
            scope.set_tag("request_id", request_id)
            scope.set_context("error_details", {
                "code": error.code,
                "message": error.message,
                "status_code": error.status_code
            })
            sentry_sdk.capture_exception(error)
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
        # Log warning
        current_app.logger.warning(f'Request {request_id}: Resource not found')
        
        # Add context to Sentry
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("error_type", "not_found")
            scope.set_tag("request_id", request_id)
            scope.set_context("request_details", {
                "url": request.url if request else "unknown",
                "method": request.method if request else "unknown"
            })
            sentry_sdk.capture_message("Resource not found", "warning")
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
        # Log warning
        current_app.logger.warning(f'Request {request_id}: Rate limit exceeded')
        
        # Add context to Sentry
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("error_type", "rate_limit")
            scope.set_tag("request_id", request_id)
            scope.set_context("request_details", {
                "url": request.url if request else "unknown",
                "method": request.method if request else "unknown"
            })
            sentry_sdk.capture_message("Rate limit exceeded", "warning")
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
        # Log error
        current_app.logger.error(f'Request {request_id} failed with unexpected error: {str(error)}')
        current_app.logger.error(traceback.format_exc())
        
        # Add context to Sentry
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("error_type", "server_error")
            scope.set_tag("request_id", request_id)
            scope.set_context("error_details", {
                "error_class": error.__class__.__name__,
                "error_message": str(error),
                "traceback": traceback.format_exc()
            })
            sentry_sdk.capture_exception(error)
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
        # Log error
        current_app.logger.error(f'Request {request_id} failed with unhandled error: {str(error)}')
        current_app.logger.error(traceback.format_exc())
        
        # Add context to Sentry
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("error_type", "unhandled")
            scope.set_tag("request_id", request_id)
            scope.set_context("error_details", {
                "error_class": error.__class__.__name__,
                "error_message": str(error),
                "traceback": traceback.format_exc()
            })
            if request:
                scope.set_context("request_details", {
                    "url": request.url,
                    "method": request.method,
                    "headers": dict(request.headers),
                    "args": dict(request.args)
                })
            sentry_sdk.capture_exception(error)
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
