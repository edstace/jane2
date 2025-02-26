from datetime import datetime
from app import db
from app.models import User, SMSContext
from sqlalchemy.exc import IntegrityError
import uuid

class UserService:
    """Service for handling user operations"""
    
    @classmethod
    def create_user(cls, user_data):
        """Create a new user"""
        try:
            user = User(
                username=user_data.get('username'),
                email=user_data.get('email'),
                first_name=user_data.get('first_name'),
                last_name=user_data.get('last_name'),
                phone_number=user_data.get('phone_number'),
                date_joined=datetime.utcnow(),
                is_active=True
            )
            
            # Set password
            user.set_password(user_data.get('password'))
            
            db.session.add(user)
            db.session.commit()
            
            # If phone number is provided, link any existing SMS contexts
            if user.phone_number:
                cls._link_sms_contexts(user)
            
            return user
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Username or email already exists")
        except Exception as e:
            db.session.rollback()
            raise e
    
    @classmethod
    def update_user(cls, user_id, user_data):
        """Update user information"""
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Update user fields
            if 'email' in user_data:
                user.email = user_data['email']
            if 'first_name' in user_data:
                user.first_name = user_data['first_name']
            if 'last_name' in user_data:
                user.last_name = user_data['last_name']
            if 'phone_number' in user_data:
                old_phone = user.phone_number
                user.phone_number = user_data['phone_number']
                
                # If phone number changed, link any SMS contexts
                if old_phone != user.phone_number and user.phone_number:
                    cls._link_sms_contexts(user)
            
            # Update password if provided
            if 'password' in user_data:
                user.set_password(user_data['password'])
            
            db.session.commit()
            return user
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Email or phone number already exists")
        except Exception as e:
            db.session.rollback()
            raise e
    
    @classmethod
    def get_user_by_id(cls, user_id):
        """Get user by ID"""
        return User.query.get(user_id)
    
    @classmethod
    def get_user_by_username(cls, username):
        """Get user by username"""
        return User.query.filter_by(username=username).first()
    
    @classmethod
    def get_user_by_email(cls, email):
        """Get user by email"""
        return User.query.filter_by(email=email).first()
    
    @classmethod
    def get_user_by_phone(cls, phone_number):
        """Get user by phone number"""
        return User.query.filter_by(phone_number=phone_number).first()
    
    @classmethod
    def authenticate_user(cls, login, password):
        """Authenticate user by username/email and password"""
        # Try to find user by username or email
        user = User.query.filter((User.username == login) | (User.email == login)).first()
        
        if user and user.check_password(password):
            # Update last login time
            user.last_login = datetime.utcnow()
            db.session.commit()
            return user
        
        return None
    
    @classmethod
    def generate_conversation_id(cls, user_id=None):
        """Generate a unique conversation ID"""
        return str(uuid.uuid4())
    
    @classmethod
    def _link_sms_contexts(cls, user):
        """Link existing SMS contexts to user account"""
        contexts = SMSContext.query.filter_by(phone_number=user.phone_number).all()
        for context in contexts:
            context.user_id = user.id
        db.session.commit()