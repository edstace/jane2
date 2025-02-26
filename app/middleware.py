import uuid
from flask import request, g, has_request_context
from werkzeug.local import LocalProxy

def request_id():
    """Get the current request ID or generate a new one"""
    if not hasattr(g, 'request_id'):
        g.request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
    return g.request_id

# Create a proxy for easier access to request_id
request_id_proxy = LocalProxy(request_id)

def init_request_id(app):
    """Initialize request ID handling for the Flask app"""
    app.before_request(request_id)

class RequestIDMiddleware:
    """Middleware to handle request ID propagation in response headers"""
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        def new_start_response(status, headers, exc_info=None):
            # Add request ID to response headers if we have a request context
            if has_request_context() and hasattr(g, 'request_id'):
                headers.append(('X-Request-ID', g.request_id))
            return start_response(status, headers, exc_info)
        return self.wsgi_app(environ, new_start_response)
