class BaseError(Exception):
    """Base exception for all custom exceptions"""
    def __init__(self, message, code=None, status_code=500):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code

class APIError(BaseError):
    """Raised when external API calls fail"""
    def __init__(self, message, code='API_ERROR', status_code=503):
        super().__init__(message, code, status_code)

class DatabaseError(BaseError):
    """Raised when database operations fail"""
    def __init__(self, message, code='DB_ERROR', status_code=500):
        super().__init__(message, code, status_code)

class ValidationError(BaseError):
    """Raised when input validation fails"""
    def __init__(self, message, code='VALIDATION_ERROR', status_code=400):
        super().__init__(message, code, status_code)

class AuthenticationError(BaseError):
    """Raised when authentication fails"""
    def __init__(self, message, code='AUTH_ERROR', status_code=401):
        super().__init__(message, code, status_code)

class RateLimitError(BaseError):
    """Raised when rate limit is exceeded"""
    def __init__(self, message, code='RATE_LIMIT_ERROR', status_code=429):
        super().__init__(message, code, status_code)
