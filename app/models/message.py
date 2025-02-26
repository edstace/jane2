from app import db
from datetime import datetime

class Message(db.Model):
    """Model for storing chat messages"""
    __tablename__ = 'message'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Message {self.id}: {self.type}>'
    
    def to_dict(self):
        """Convert message to dictionary"""
        return {
            'id': self.id,
            'content': self.content,
            'type': self.type,
            'timestamp': self.timestamp.isoformat()
        }