from twilio.rest import Client
from flask import current_app
from app import db
from app.models import SMSContext

class SMSService:
    """Service for handling SMS functionality"""
    
    @classmethod
    def send_sms(cls, to_number, message):
        """Send SMS using Twilio"""
        if current_app.config['ENV'] != 'production':
            # Mock response in development
            current_app.logger.info(f"[DEV] SMS would be sent to {to_number}: {message}")
            return True
            
        try:
            client = Client(
                current_app.config['TWILIO_ACCOUNT_SID'],
                current_app.config['TWILIO_AUTH_TOKEN']
            )
            message = client.messages.create(
                body=message,
                from_=current_app.config['TWILIO_PHONE_NUMBER'],
                to=to_number
            )
            current_app.logger.info(f"SMS sent to {to_number}: {message.sid}")
            return True
        except Exception as e:
            current_app.logger.error(f"Error sending SMS: {str(e)}")
            return False
    
    @classmethod
    def get_context(cls, phone_number):
        """Get conversation context for a phone number"""
        context = SMSContext.query.filter_by(phone_number=phone_number)\
            .order_by(SMSContext.timestamp.desc())\
            .limit(5)\
            .all()
        
        return [{"role": msg.role, "content": msg.content} for msg in reversed(context)]
    
    @classmethod
    def save_context(cls, phone_number, user_message, bot_response):
        """Save SMS conversation context"""
        # Add new messages
        user_msg = SMSContext(
            phone_number=phone_number,
            role="user",
            content=user_message
        )
        bot_msg = SMSContext(
            phone_number=phone_number,
            role="assistant",
            content=bot_response
        )
        db.session.add(user_msg)
        db.session.add(bot_msg)
        
        # Keep only last 5 messages per phone number
        old_messages = SMSContext.query.filter_by(phone_number=phone_number)\
            .order_by(SMSContext.timestamp.desc())\
            .offset(5)\
            .all()
        
        for msg in old_messages:
            db.session.delete(msg)
        
        db.session.commit()
    
    @classmethod
    def check_confirmation(cls, phone_number):
        """Check if user has a pending confirmation"""
        context = SMSContext.query.filter_by(
            phone_number=phone_number,
            awaiting_confirmation=True
        ).first()
        return context
    
    @classmethod
    def save_pending(cls, phone_number, message):
        """Save message pending confirmation"""
        context = SMSContext(
            phone_number=phone_number,
            role="user",
            content="Awaiting confirmation",
            awaiting_confirmation=True,
            original_message=message
        )
        db.session.add(context)
        db.session.commit()
        return context