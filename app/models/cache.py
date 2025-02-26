from app import db
from datetime import datetime

class Cache(db.Model):
    """Model for caching API responses"""
    __tablename__ = 'cache'
    
    id = db.Column(db.String(255), primary_key=True)
    response = db.Column(db.Text, nullable=False)
    expires = db.Column(db.DateTime, nullable=False)
    
    def __repr__(self):
        return f'<Cache {self.id}>'
    
    def is_expired(self):
        """Check if cache entry is expired"""
        return self.expires < datetime.utcnow()