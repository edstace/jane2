from flask import Blueprint, request, jsonify, current_app, g, session
from datetime import datetime
from app import limiter, csrf
from flask_login import current_user
from app.utils.validators import ValidationUtils
from app.services.ai_service import AIService
from app.services.message_service import MessageService
from app.services.user_service import UserService
from app.exceptions import ValidationError, APIError

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
@limiter.limit("30 per minute")  # More lenient rate limit
@csrf.exempt  # Exempt this route from CSRF protection since we handle it in JS
def chat():
    """Handle chat requests with validation and error handling"""
    current_app.logger.info(f"Processing chat request {g.request_id}")
    request_data = request.get_json()
    ValidationUtils.log_request(request_data)
    
    user_message = request_data.get('message', '')
    confirmed = request_data.get('confirmed', False)
    conversation_id = request_data.get('conversation_id')
    
    # Get or create conversation ID
    if not conversation_id and current_user.is_authenticated:
        conversation_id = MessageService.start_new_conversation(current_user.id)
    elif not conversation_id:
        # For anonymous users, use session ID as a temporary conversation ID
        if 'session_id' not in session:
            session['session_id'] = UserService.generate_conversation_id()
        conversation_id = session['session_id']
    
    if not user_message:
        raise ValidationError("Message cannot be empty")
    
    # Security checks
    if ValidationUtils.contains_sensitive_info(user_message):
        raise ValidationError(
            "Your message appears to contain sensitive personal information. Please remove any personal details before sending.",
            code="SENSITIVE_INFO"
        )
    
    if ValidationUtils.contains_harmful_interactions(user_message):
        raise ValidationError(
            "Your message contains language that may be harmful or dangerous. Please reconsider your wording or seek professional assistance if needed.",
            code="HARMFUL_CONTENT"
        )
    
    if ValidationUtils.contains_disability_info(user_message) and not confirmed:
        raise ValidationError(
            "Your message includes disability-related information. Please ensure you are comfortable sharing these details.",
            code="REQUIRES_CONFIRMATION"
        )
    
    try:
        # Get response from OpenAI with context
        response_text = AIService.get_job_coaching_advice(user_message, request_data.get('context'))
    except Exception as e:
        current_app.logger.error(f"OpenAI API error for request {g.request_id}: {str(e)}")
        raise APIError("Failed to get AI response. Please try again later.")
    
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
    
    user_id = current_user.id if current_user.is_authenticated else None
    MessageService.cache_message(user_msg, user_id, conversation_id)
    MessageService.cache_message(bot_msg, user_id, conversation_id)
    
    response = {'response': response_text}
    ValidationUtils.log_response(response)
    current_app.logger.info(f"Successfully processed chat request {g.request_id}")
    return jsonify(response)
