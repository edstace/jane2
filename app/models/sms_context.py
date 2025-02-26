from app import db
from datetime import datetime

class SMSContext(db.Model):
    """Model for storing SMS conversation context"""
    __tablename__ = 'sms_context'
    
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    awaiting_confirmation = db.Column(db.Boolean, default=False)
    original_message = db.Column(db.Text)
    
    def __repr__(self):
        return f'<SMSContext {self.id}: {self.role}>'
    
    def to_dict(self):
        """Convert SMS context to dictionary"""
        return {
            'role': self.role,
            'content': self.content
        }