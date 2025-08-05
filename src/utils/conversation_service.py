"""
Conversation History Service for Flight Booking Agent (SQLite)
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

from .models import ConversationHistory, ConversationEntry
from .database import db_manager

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing conversation history using SQLite."""
    
    def __init__(self):
        """Initialize the conversation service."""
        self.db = db_manager
        logger.info("Conversation service initialized with SQLite database")
    
    def save_conversation(self, conversation: ConversationHistory) -> bool:
        """Save a conversation to database."""
        try:
            # Create conversation in database
            success = self.db.create_conversation(conversation.thread_id, conversation.user_id)
            
            if success and conversation.entries:
                # Add all entries
                for entry in conversation.entries:
                    self.db.add_conversation_entry(
                        thread_id=entry.thread_id,
                        user_id=entry.user_id,
                        user_input=entry.user_input,
                        session_id=entry.session_id,
                        metadata=entry.metadata
                    )
            
            logger.info(f"Conversation saved for thread {conversation.thread_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save conversation for thread {conversation.thread_id}: {e}")
            return False
    
    def load_conversation(self, thread_id: str) -> Optional[ConversationHistory]:
        """Load a conversation from database."""
        try:
            conversation_data = self.db.get_conversation(thread_id)
            if not conversation_data:
                logger.info(f"No conversation found for thread {thread_id}")
                return None
            
            # Convert database entries to ConversationEntry objects
            entries = []
            for entry_data in conversation_data.get('entries', []):
                entry = ConversationEntry(
                    timestamp=datetime.fromisoformat(entry_data['timestamp'].replace('Z', '+00:00')),
                    user_input=entry_data['user_input'],
                    thread_id=entry_data['thread_id'],
                    user_id=entry_data['user_id'],
                    session_id=entry_data['session_id'],
                    metadata=entry_data.get('metadata', {})
                )
                entries.append(entry)
            
            # Create ConversationHistory object
            conversation = ConversationHistory(
                thread_id=conversation_data['thread_id'],
                user_id=conversation_data['user_id'],
                entries=entries
            )
            
            logger.info(f"Conversation loaded for thread {thread_id} with {len(entries)} entries")
            return conversation
            
        except Exception as e:
            logger.error(f"Failed to load conversation for thread {thread_id}: {e}")
            return None
    
    def create_or_load_conversation(self, thread_id: str, user_id: str) -> ConversationHistory:
        """Create a new conversation or load existing one."""
        existing = self.load_conversation(thread_id)
        if existing:
            return existing
        
        # Create new conversation
        conversation = ConversationHistory(
            thread_id=thread_id,
            user_id=user_id
        )
        
        # Save the new conversation
        self.save_conversation(conversation)
        logger.info(f"Created new conversation for thread {thread_id}")
        return conversation
    
    def add_conversation_entry(self, thread_id: str, user_input: str, user_id: str, 
                             session_id: str = None, metadata: Dict[str, Any] = None) -> bool:
        """Add a new entry to an existing conversation."""
        try:
            success = self.db.add_conversation_entry(
                thread_id=thread_id,
                user_id=user_id,
                user_input=user_input,
                session_id=session_id,
                metadata=metadata
            )
            
            if success:
                logger.info(f"Conversation entry added for thread {thread_id}")
            else:
                logger.warning(f"Failed to add conversation entry for thread {thread_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to add conversation entry for thread {thread_id}: {e}")
            return False
    
    def get_conversation_summary(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of a conversation."""
        return self.db.get_conversation_summary(thread_id)
    
    def list_conversations(self, user_id: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """List all conversations, optionally filtered by user_id."""
        return self.db.list_conversations(user_id=user_id, limit=limit)
    
    def delete_conversation(self, thread_id: str) -> bool:
        """Delete a conversation."""
        return self.db.delete_conversation(thread_id)
    
    def cleanup_old_conversations(self, days_old: int = 30) -> int:
        """Clean up conversations older than specified days."""
        return self.db.cleanup_old_conversations(days_old)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        return self.db.get_statistics()
    
    def get_conversation_entries(self, thread_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get conversation entries for a thread."""
        return self.db.get_conversation_entries(thread_id, limit)


# Global instance
conversation_service = ConversationService() 