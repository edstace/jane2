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

class RequestIDMiddleware:
    """Middleware to handle request ID generation and propagation"""
    def __init__(self, app):
        self.app = app
        self.app.before_request(self._before_request)

    def _before_request(self):
        """Ensure request ID is set before request processing"""
        request_id()

    def __call__(self, environ, start_response):
        def new_start_response(status, headers, exc_info=None):
            # Add request ID to response headers if we have a request context
            if has_request_context() and hasattr(g, 'request_id'):
                headers.append(('X-Request-ID', g.request_id))
            return start_response(status, headers, exc_info)
        return self.app(environ, new_start_response)
