from flask import Blueprint, request, current_app, g
from twilio.twiml.messaging_response import MessagingResponse
from app import csrf
from app.utils.validators import ValidationUtils
from app.services.ai_service import AIService
from app.services.sms_service import SMSService
from app.exceptions import ValidationError, APIError, DatabaseError

sms_bp = Blueprint('sms', __name__)

@sms_bp.route('', methods=['POST'])
@csrf.exempt  # Exempt Twilio webhooks from CSRF protection
def handle_sms():
    """Handle incoming SMS messages"""
    # Get incoming message details
    current_app.logger.info(f"Processing SMS request {g.request_id}")
    from_number = request.values.get('From', '')
    message_body = request.values.get('Body', '').strip().lower()
    
    if not message_body:
        return str(MessagingResponse())

    try:
        # Check for pending confirmation
        pending = SMSService.check_confirmation(from_number)
        current_app.logger.info(f"Request {g.request_id}: Checking confirmation for {from_number}: {pending is not None}")
        
        if pending:
            resp = MessagingResponse()
            current_app.logger.info(f"Request {g.request_id}: Processing confirmation: {message_body}")
            
            if message_body in ['y', 'yes']:
                current_app.logger.info(f"Request {g.request_id}: User confirmed")
                try:
                    # Process the original message
                    context = SMSService.get_context(from_number)
                    response_text = AIService.get_job_coaching_advice(pending.original_message, context)
                    SMSService.save_context(from_number, pending.original_message, response_text)
                except Exception as e:
                    current_app.logger.error(f"Request {g.request_id} API error: {str(e)}")
                    raise APIError("Failed to process confirmed message")
                
                # Clear pending confirmation
                pending.awaiting_confirmation = False
                current_app.logger.info(f"Request {g.request_id}: Cleared confirmation")
                
                resp.message(response_text)
            elif message_body in ['n', 'no']:
                current_app.logger.info(f"Request {g.request_id}: User declined")
                pending.awaiting_confirmation = False
                resp.message("Message cancelled.")
            else:
                resp.message("Please reply with 'y' for yes or 'n' for no to confirm sending your message.")
            
            return str(resp)
        
        # Log incoming message
        current_app.logger.info(f"Request {g.request_id}: SMS from {from_number}")
        
        # Security checks
        if ValidationUtils.contains_sensitive_info(message_body):
            raise ValidationError(
                "Please avoid sharing sensitive personal information.",
                code="SENSITIVE_INFO"
            )
        
        if ValidationUtils.contains_harmful_interactions(message_body):
            raise ValidationError(
                "Message contains harmful content. Please seek professional help if needed.",
                code="HARMFUL_CONTENT"
            )
        
        if ValidationUtils.contains_disability_info(message_body):
            try:
                SMSService.save_pending(from_number, message_body)
            except Exception as e:
                current_app.logger.error(f"Request {g.request_id} DB error: {str(e)}")
                raise DatabaseError("Failed to save pending confirmation")
            
            resp = MessagingResponse()
            resp.message(
                'Your message includes disability-related information. '
                'Please ensure you are comfortable sharing these details. '
                'Reply "y" to confirm sending this information, or "n" to cancel.'
            )
            return str(resp)
        
        try:
            # Get context and generate response
            context = SMSService.get_context(from_number)
            response_text = AIService.get_job_coaching_advice(message_body, context)
            SMSService.save_context(from_number, message_body, response_text)
        except Exception as e:
            current_app.logger.error(f"Request {g.request_id} processing error: {str(e)}")
            raise APIError("Failed to process message")
        
        # Create response
        resp = MessagingResponse()
        resp.message(response_text)
        current_app.logger.info(f"Request {g.request_id} completed successfully")
        return str(resp)
        
    except (ValidationError, APIError, DatabaseError) as e:
        # Let these propagate to global handler
        raise
    except Exception as e:
        current_app.logger.error(f"Request {g.request_id} unexpected error: {str(e)}")
        resp = MessagingResponse()
        resp.message("I apologize, but I'm having trouble processing your request. Please try again later.")
        return str(resp)
