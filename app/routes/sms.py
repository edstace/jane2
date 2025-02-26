from flask import Blueprint, request, current_app
from twilio.twiml.messaging_response import MessagingResponse
from app import csrf
from app.utils.validators import ValidationUtils
from app.services.ai_service import AIService
from app.services.sms_service import SMSService

sms_bp = Blueprint('sms', __name__)

@sms_bp.route('', methods=['POST'])
@csrf.exempt  # Exempt Twilio webhooks from CSRF protection
def handle_sms():
    """Handle incoming SMS messages"""
    try:
        # Get incoming message details
        from_number = request.values.get('From', '')
        message_body = request.values.get('Body', '').strip().lower()
        
        if not message_body:
            return str(MessagingResponse())

        # Check for pending confirmation
        pending = SMSService.check_confirmation(from_number)
        current_app.logger.info(f"Checking pending confirmation for {from_number}: {pending is not None}")
        
        if pending:
            resp = MessagingResponse()
            current_app.logger.info(f"Processing confirmation response: {message_body}")
            
            if message_body in ['y', 'yes']:
                current_app.logger.info("User confirmed sending disability information")
                # Process the original message
                context = SMSService.get_context(from_number)
                response_text = AIService.get_job_coaching_advice(pending.original_message, context)
                SMSService.save_context(from_number, pending.original_message, response_text)
                
                # Clear pending confirmation
                pending.awaiting_confirmation = False
                current_app.logger.info("Cleared pending confirmation and saved context")
                
                resp.message(response_text)
            elif message_body in ['n', 'no']:
                current_app.logger.info("User declined sending disability information")
                # Clear pending confirmation
                pending.awaiting_confirmation = False
                current_app.logger.info("Cleared pending confirmation")
                
                resp.message("Message cancelled.")
            else:
                current_app.logger.info("Invalid confirmation response, requesting y/n")
                resp.message("Please reply with 'y' for yes or 'n' for no to confirm sending your message.")
            
            response_str = str(resp)
            current_app.logger.info(f"Sending confirmation response: {response_str}")
            return response_str
        
        # Log incoming message
        current_app.logger.info(f"Received SMS from {from_number}: {message_body}")
        
        # Check for sensitive/harmful content
        if ValidationUtils.contains_sensitive_info(message_body):
            current_app.logger.info("Sensitive info detected")
            response_text = 'Please avoid sharing sensitive personal information. This information will not be processed for your privacy and security.'
        elif ValidationUtils.contains_harmful_interactions(message_body):
            current_app.logger.info("Harmful content detected")
            response_text = 'I noticed concerning content in your message. For your safety, this message will not be processed. Please seek professional help if needed.'
        elif ValidationUtils.contains_disability_info(message_body):
            current_app.logger.info("Disability info detected, requesting confirmation")
            SMSService.save_pending(from_number, message_body)
            response_text = ('Your message includes disability-related information. '
                           'Please ensure you are comfortable sharing these details. '
                           'Reply "y" to confirm sending this information, or "n" to cancel.')
        else:
            # Get context and generate response
            context = SMSService.get_context(from_number)
            response_text = AIService.get_job_coaching_advice(message_body, context)
            SMSService.save_context(from_number, message_body, response_text)
        
        # Create and log TwiML response
        resp = MessagingResponse()
        resp.message(response_text)
        response_str = str(resp)
        current_app.logger.info(f"Sending response: {response_str}")
        return response_str
        
    except Exception as e:
        current_app.logger.error(f"SMS handling error: {str(e)}")
        resp = MessagingResponse()
        resp.message("I apologize, but I'm having trouble processing your request. Please try again later.")
        return str(resp)