import re
import json
from flask import current_app

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class ValidationUtils:
    """Validation utilities for message content"""
    
    @staticmethod
    def contains_sensitive_info(message):
        """
        Checks the message for patterns that indicate sensitive personal information.
        Returns True if sensitive data is detected, else False.
        """
        patterns = {
            'email': r'[\w\.-]+@[\w\.-]+',
            'phone': r'\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        }
        
        for pattern_type, pattern in patterns.items():
            if re.search(pattern, message):
                current_app.logger.warning(f"Sensitive information detected: {pattern_type}")
                return True
        return False
    
    @staticmethod
    def contains_harmful_interactions(message):
        """
        Checks the message for language that might indicate harmful or dangerous content.
        Returns True if harmful content is detected, else False.
        """
        harmful_keywords = [
            "kill", "die", "suicide", "self harm", "self-harm",
            "hurt myself", "hurt others", "violence", "abuse", "murder", "attack"
        ]
        lower_message = message.lower()
        for keyword in harmful_keywords:
            if keyword in lower_message:
                current_app.logger.warning(f"Harmful content detected: {keyword}")
                return True
        return False
    
    @staticmethod
    def contains_disability_info(message):
        """
        Checks the message for disability-related keywords.
        This is meant to prompt users to be cautious about sharing personal health or disability details.
        Returns True if disability-related content is detected, else False.
        """
        disability_keywords = [
            "disability", "disabled", "autism", "adhd", "cerebral palsy", 
            "dyslexia", "blind", "deaf", "wheelchair", "mobility", 
            "chronic illness", "mental health", "amputation", "paraplegia", 
            "quadriplegia", "neurodiverse", "ptsd", "anxiety", "depression",
            "ocd", "bipolar", "schizophrenia", "trauma"
        ]
        lower_message = message.lower()
        for keyword in disability_keywords:
            if keyword in lower_message:
                current_app.logger.info(f"Disability-related content detected: {keyword}")
                return True
        return False
    
    @staticmethod
    def log_request(request_data):
        """Log request data"""
        current_app.logger.info(f"Request: {json.dumps(request_data, default=str)}")
    
    @staticmethod
    def log_response(response_data):
        """Log response data"""
        current_app.logger.info(f"Response: {json.dumps(response_data, default=str)}")