from datetime import datetime
from app import db
from app.models import Message, Cache

class MessageService:
    """Service for handling chat message operations"""
    
    @classmethod
    def cache_message(cls, message_data):
        """Add message to database"""
        try:
            message = Message(
                content=message_data['content'],
                type=message_data['type'],
                timestamp=datetime.fromisoformat(message_data['timestamp']) 
                    if isinstance(message_data['timestamp'], str) 
                    else message_data['timestamp']
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
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    @classmethod
    def clear_history(cls):
        """Clear all chat messages and cache"""
        try:
            # Clear message history
            Message.query.delete()
            
            # Clear response cache
            Cache.query.delete()
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    @classmethod
    def get_message_history(cls, limit=5):
        """Get recent message history"""
        messages = Message.query\
            .order_by(Message.timestamp.desc())\
            .limit(limit)\
            .all()
        
        return [msg.to_dict() for msg in reversed(messages)]