from datetime import datetime
from app import db
from app.models import Message, Cache
from app.services.user_service import UserService

class MessageService:
    """Service for handling chat message operations"""
    
    @classmethod
    def cache_message(cls, message_data, user_id=None, conversation_id=None):
        """Add message to database"""
        try:
            message = Message(
                content=message_data['content'],
                type=message_data['type'],
                timestamp=datetime.fromisoformat(message_data['timestamp']) 
                    if isinstance(message_data['timestamp'], str) 
                    else message_data['timestamp'],
                user_id=user_id,
                conversation_id=conversation_id
            )
            db.session.add(message)
            
            # If no conversation ID, use older behavior (keep only last 5 messages)
            if not conversation_id:
                # Keep only last 5 messages for anonymous users
                filter_query = Message.query
                if user_id:
                    filter_query = filter_query.filter_by(user_id=user_id)
                else:
                    filter_query = filter_query.filter_by(user_id=None)
                
                old_messages = filter_query\
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
    def clear_history(cls, user_id=None, conversation_id=None):
        """Clear chat messages and cache"""
        try:
            # Clear message history based on filters
            query = Message.query
            if user_id:
                query = query.filter_by(user_id=user_id)
            if conversation_id:
                query = query.filter_by(conversation_id=conversation_id)
            
            query.delete(synchronize_session=False)
            
            # Clear response cache
            Cache.query.delete()
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    @classmethod
    def get_message_history(cls, user_id=None, conversation_id=None, limit=50):
        """Get message history for a user or conversation"""
        query = Message.query
        
        # Apply filters
        if user_id:
            query = query.filter_by(user_id=user_id)
        if conversation_id:
            query = query.filter_by(conversation_id=conversation_id)
        
        messages = query\
            .order_by(Message.timestamp.desc())\
            .limit(limit)\
            .all()
        
        return [msg.to_dict() for msg in reversed(messages)]
    
    @classmethod
    def get_conversations(cls, user_id):
        """Get all conversations for a user"""
        # Get distinct conversation IDs for this user
        conversations = db.session.query(Message.conversation_id)\
            .filter_by(user_id=user_id)\
            .filter(Message.conversation_id.isnot(None))\
            .distinct()\
            .all()
        
        result = []
        for conv in conversations:
            conv_id = conv[0]
            # Get the latest message for this conversation
            latest_message = Message.query\
                .filter_by(conversation_id=conv_id)\
                .order_by(Message.timestamp.desc())\
                .first()
            
            if latest_message:
                result.append({
                    'id': conv_id,
                    'last_message': latest_message.content[:50] + '...' if len(latest_message.content) > 50 else latest_message.content,
                    'last_updated': latest_message.timestamp.isoformat(),
                    'message_count': Message.query.filter_by(conversation_id=conv_id).count()
                })
        
        # Sort by last updated
        result.sort(key=lambda x: x['last_updated'], reverse=True)
        return result
    
    @classmethod
    def start_new_conversation(cls, user_id):
        """Start a new conversation for a user"""
        return UserService.generate_conversation_id(user_id)