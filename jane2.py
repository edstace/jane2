from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.pool import QueuePool
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime, timedelta
import openai
import re
import os
import logging
from logging.handlers import RotatingFileHandler
import json
from functools import wraps

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
# Configure SQLAlchemy with psycopg2
db_url = os.getenv('DATABASE_URL')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)
elif db_url.startswith('postgresql://'):
    db_url = db_url

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Configure SQLAlchemy engine options based on environment
if os.getenv('FLASK_ENV') == 'production':
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'poolclass': QueuePool,
        'pool_pre_ping': True,
        'pool_size': 5,
        'max_overflow': 10,
        'pool_timeout': 30,
        'pool_recycle': 1800,  # Recycle connections after 30 minutes
        'connect_args': {
            'sslmode': 'require',
            'connect_timeout': 10
        }
    }

db = SQLAlchemy(app)

# Define models
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Cache(db.Model):
    id = db.Column(db.String(255), primary_key=True)
    response = db.Column(db.Text, nullable=False)
    expires = db.Column(db.DateTime, nullable=False)

class SMSContext(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    awaiting_confirmation = db.Column(db.Boolean, default=False)
    original_message = db.Column(db.Text)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Initialize Twilio client only in production
if os.getenv('FLASK_ENV') == 'production':
    twilio_client = Client(
        os.getenv('TWILIO_ACCOUNT_SID'),
        os.getenv('TWILIO_AUTH_TOKEN')
    )
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Initialize security extensions
if os.getenv('FLASK_ENV') == 'production':
    Talisman(app, content_security_policy={
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'"],
        'style-src': ["'self'", "'unsafe-inline'", "fonts.googleapis.com"],
        'font-src': ["'self'", "fonts.gstatic.com"],
        'img-src': ["'self'", "data:", "https:"],
    })
csrf = CSRFProtect(app)

# Initialize rate limiter with memory storage
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[os.getenv('RATELIMIT_DEFAULT', '1000 per hour')],
    storage_uri="memory://"
)

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

file_handler = RotatingFileHandler(
    'logs/jane.log', 
    maxBytes=10240, 
    backupCount=10
)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# Initialize OpenAI client only in production
if os.getenv('FLASK_ENV') == 'production':
    openai.api_key = os.getenv('OPENAI_API_KEY')

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

def cache_response(func):
    """Decorator to cache API responses"""
    @wraps(func)
    def wrapper(user_message, context=None):
        # Only cache responses without context
        if not context:
            cache_key = f"response:{hash(user_message)}"
            cached = Cache.query.get(cache_key)
            
            if cached and cached.expires > datetime.utcnow():
                app.logger.info("Cache hit for message")
                return cached.response
            
            response = func(user_message, context)
            
            # Cache for 1 hour
            if cached:
                cached.response = response
                cached.expires = datetime.utcnow() + timedelta(hours=1)
            else:
                cached = Cache(
                    id=cache_key,
                    response=response,
                    expires=datetime.utcnow() + timedelta(hours=1)
                )
                db.session.add(cached)
            
            db.session.commit()
            return response
        
        return func(user_message, context)
    return wrapper

def log_request(request_data):
    """Log request data"""
    app.logger.info(f"Request: {json.dumps(request_data, default=str)}")

def log_response(response_data):
    """Log response data"""
    app.logger.info(f"Response: {json.dumps(response_data, default=str)}")

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
            app.logger.warning(f"Sensitive information detected: {pattern_type}")
            return True
    return False

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
            app.logger.warning(f"Harmful content detected: {keyword}")
            return True
    return False

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
            app.logger.info(f"Disability-related content detected: {keyword}")
            return True
    return False

def get_job_coaching_advice(user_message, context=None):
    """Get job coaching advice using OpenAI"""
    if os.getenv('FLASK_ENV') == 'production':
        try:
            messages = [
                {"role": "system", "content": "You are Jane, a professional job coach. You help people with career advice, resume writing, interview preparation, and professional development. Format your responses using this specific markdown style:\n\n1. Main sections start with '### Step N: Title'\n2. Sub-sections use '#### Title'\n3. Use bullet points (-) for lists\n4. Use **bold** for emphasis and key terms\n5. Use ```plaintext blocks for examples and templates\n6. Keep content structured and hierarchical\n7. Include specific examples in code blocks\n8. Break long responses into clear, numbered steps\n9. Use consistent formatting throughout\n\nExample format:\n### Step 1: Section Title\nIntroductory text\n\n- **Key Point**: Description\n- **Another Point**: Description\n\n#### Sub-section\n```plaintext\nExample or template here\n```\n\nKeep responses focused, practical, and actionable."}
            ]
            
            # Add conversation context if provided
            if context:
                messages.extend(context)
            
            # Add user's message
            messages.append({"role": "user", "content": user_message})
            
            # Get response from OpenAI using v1.0.0+ syntax
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            app.logger.error(f"OpenAI API error: {str(e)}")
            raise
    else:
        # Development mock response
        return f"Development mode response: You said '{user_message}'"

def send_sms(to_number, message):
    """Send SMS using Twilio"""
    try:
        message = twilio_client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_number
        )
        app.logger.info(f"SMS sent to {to_number}: {message.sid}")
        return True
    except Exception as e:
        app.logger.error(f"Error sending SMS: {str(e)}")
        return False

def get_sms_context(phone_number):
    """Get conversation context for a phone number"""
    context = SMSContext.query.filter_by(phone_number=phone_number)\
        .order_by(SMSContext.timestamp.desc())\
        .limit(5)\
        .all()
    
    return [{"role": msg.role, "content": msg.content} for msg in reversed(context)]

def save_sms_context(phone_number, user_message, bot_response):
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

def check_sms_confirmation(phone_number):
    """Check if user has a pending confirmation"""
    context = SMSContext.query.filter_by(
        phone_number=phone_number,
        awaiting_confirmation=True
    ).first()
    return context

def save_pending_sms(phone_number, message):
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

@app.route('/sms', methods=['POST'])
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
        pending = check_sms_confirmation(from_number)
        app.logger.info(f"Checking pending confirmation for {from_number}: {pending is not None}")
        
        if pending:
            resp = MessagingResponse()
            app.logger.info(f"Processing confirmation response: {message_body}")
            
            if message_body in ['y', 'yes']:
                app.logger.info("User confirmed sending disability information")
                # Process the original message
                context = get_sms_context(from_number)
                response_text = get_job_coaching_advice(pending.original_message, context)
                save_sms_context(from_number, pending.original_message, response_text)
                
                # Clear pending confirmation
                pending.awaiting_confirmation = False
                db.session.commit()
                app.logger.info("Cleared pending confirmation and saved context")
                
                resp.message(response_text)
            elif message_body in ['n', 'no']:
                app.logger.info("User declined sending disability information")
                # Clear pending confirmation
                pending.awaiting_confirmation = False
                db.session.commit()
                app.logger.info("Cleared pending confirmation")
                
                resp.message("Message cancelled. How else can I help you?")
            else:
                app.logger.info("Invalid confirmation response, requesting y/n")
                resp.message("Please reply with 'y' for yes or 'n' for no to confirm sending your message.")
            
            response_str = str(resp)
            app.logger.info(f"Sending confirmation response: {response_str}")
            return response_str
        
        # Log incoming message
        app.logger.info(f"Received SMS from {from_number}: {message_body}")
        
        # Check for sensitive/harmful content
        if contains_sensitive_info(message_body):
            app.logger.info("Sensitive info detected")
            response_text = 'Please avoid sharing sensitive personal information. This information will not be processed for your privacy and security.'
        elif contains_harmful_interactions(message_body):
            app.logger.info("Harmful content detected")
            response_text = 'I noticed concerning content in your message. For your safety, this message will not be processed. Please seek professional help if needed.'
        elif contains_disability_info(message_body):
            app.logger.info("Disability info detected, requesting confirmation")
            save_pending_sms(from_number, message_body)
            response_text = ('Your message includes disability-related information. '
                           'Please ensure you are comfortable sharing these details. '
                           'Reply "y" to confirm sending this information, or "n" to cancel.')
        else:
            # Get context and generate response
            context = get_sms_context(from_number)
            response_text = get_job_coaching_advice(message_body, context)
            save_sms_context(from_number, message_body, response_text)
        
        # Create and log TwiML response
        resp = MessagingResponse()
        resp.message(response_text)
        response_str = str(resp)
        app.logger.info(f"Sending response: {response_str}")
        return response_str
        
    except Exception as e:
        app.logger.error(f"SMS handling error: {str(e)}")
        resp = MessagingResponse()
        resp.message("I apologize, but I'm having trouble processing your request. Please try again later.")
        return str(resp)

@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files with caching headers"""
    response = send_from_directory('static', path)
    response.headers['Cache-Control'] = 'public, max-age=31536000'
    return response

@app.route('/')
def home():
    """Serve home page"""
    return render_template('index.html')

def cache_message(message_data):
    """Add message to database"""
    message = Message(
        content=message_data['content'],
        type=message_data['type'],
        timestamp=datetime.fromisoformat(message_data['timestamp']) if isinstance(message_data['timestamp'], str) else message_data['timestamp']
    )
    db.session.add(message)
    
    # Keep only last 5 messages
    old_messages = Message.query\
        .order_by(Message.timestamp.desc())\
        .offset(5)\
        .all()
    
    for msg in old_messages:
        db.session.delete(msg)
    
    db.session.commit()

@app.route('/clear-chat', methods=['POST'])
@csrf.exempt  # Allow CSRF for this endpoint since it's just clearing cache
def clear_chat():
    """Clear all cached messages and responses"""
    try:
        # Clear message history
        Message.query.delete()
        
        # Clear response cache
        Cache.query.delete()
        
        db.session.commit()
        app.logger.info("Chat history and caches cleared")
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error clearing chat: {str(e)}")
        return jsonify({'error': 'Failed to clear chat history'}), 500

@app.route('/chat', methods=['POST'])
@limiter.limit("30 per minute")  # More lenient rate limit
def chat():
    """Handle chat requests with validation and error handling"""
    try:
        request_data = request.get_json()
        log_request(request_data)
        
        user_message = request_data.get('message', '')
        confirmed = request_data.get('confirmed', False)
        
        if not user_message:
            raise ValidationError("Message cannot be empty")
        
        # Security checks
        if contains_sensitive_info(user_message):
            response = {
                'warning': 'Your message appears to contain sensitive personal information. Please remove any personal details before sending.'
            }
            log_response(response)
            return jsonify(response)
        
        if contains_harmful_interactions(user_message):
            response = {
                'warning': 'Your message contains language that may be harmful or dangerous. Please reconsider your wording or seek professional assistance if needed.'
            }
            log_response(response)
            return jsonify(response)
        
        if contains_disability_info(user_message) and not confirmed:
            response = {
                'warning': ('Your message includes disability-related information. '
                           'Please ensure you are comfortable sharing these details and avoid including overly personal or identifying details if not necessary.'),
                'requiresConfirmation': True
            }
            log_response(response)
            return jsonify(response)
        
        # Get response from OpenAI with context
        response_text = get_job_coaching_advice(user_message, request_data.get('context'))
        
        # Cache messages
        user_msg = {
            'content': user_message,
            'type': 'user-message',
            'timestamp': request_data.get('timestamp')
        }
        bot_msg = {
            'content': response_text,
            'type': 'bot-message',
            'timestamp': datetime.utcnow().isoformat()
        }
        cache_message(user_msg)
        cache_message(bot_msg)
        
        response = {'response': response_text}
        log_response(response)
        return jsonify(response)
        
    except ValidationError as e:
        app.logger.warning(f"Validation error: {str(e)}")
        return jsonify({'warning': str(e)}), 400
        
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            'warning': 'An unexpected error occurred. Please try again later.'
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    app.logger.error(f"404 error: {request.url}")
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(429)
def ratelimit_handler(error):
    app.logger.warning(f"Rate limit exceeded: {request.remote_addr}")
    return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"500 error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == "__main__":
    app.run(debug=os.getenv('FLASK_ENV') == 'development')
