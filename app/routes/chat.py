from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from app import limiter
from app.utils.validators import ValidationUtils, ValidationError
from app.services.ai_service import AIService
from app.services.message_service import MessageService

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
@limiter.limit("30 per minute")  # More lenient rate limit
def chat():
    """Handle chat requests with validation and error handling"""
    try:
        request_data = request.get_json()
        ValidationUtils.log_request(request_data)
        
        user_message = request_data.get('message', '')
        confirmed = request_data.get('confirmed', False)
        
        if not user_message:
            raise ValidationError("Message cannot be empty")
        
        # Security checks
        if ValidationUtils.contains_sensitive_info(user_message):
            response = {
                'warning': 'Your message appears to contain sensitive personal information. Please remove any personal details before sending.'
            }
            ValidationUtils.log_response(response)
            return jsonify(response)
        
        if ValidationUtils.contains_harmful_interactions(user_message):
            response = {
                'warning': 'Your message contains language that may be harmful or dangerous. Please reconsider your wording or seek professional assistance if needed.'
            }
            ValidationUtils.log_response(response)
            return jsonify(response)
        
        if ValidationUtils.contains_disability_info(user_message) and not confirmed:
            response = {
                'warning': ('Your message includes disability-related information. '
                          'Please ensure you are comfortable sharing these details and avoid including overly personal or identifying details if not necessary.'),
                'requiresConfirmation': True
            }
            ValidationUtils.log_response(response)
            return jsonify(response)
        
        # Get response from OpenAI with context
        response_text = AIService.get_job_coaching_advice(user_message, request_data.get('context'))
        
        # Cache messages
        user_msg = {
            'content': user_message,
            'type': 'user-message',
            'timestamp': request_data.get('timestamp', datetime.utcnow().isoformat())
        }
        bot_msg = {
            'content': response_text,
            'type': 'bot-message',
            'timestamp': datetime.utcnow().isoformat()
        }
        MessageService.cache_message(user_msg)
        MessageService.cache_message(bot_msg)
        
        response = {'response': response_text}
        ValidationUtils.log_response(response)
        return jsonify(response)
        
    except ValidationError as e:
        current_app.logger.warning(f"Validation error: {str(e)}")
        return jsonify({'warning': str(e)}), 400
        
    except Exception as e:
        current_app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            'warning': 'An unexpected error occurred. Please try again later.'
        }), 500