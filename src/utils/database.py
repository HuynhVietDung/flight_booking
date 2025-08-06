"""
Database management for Flight Booking Agent
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database manager for conversation history."""
    
    def __init__(self, db_path: str = "data/conversations.db"):
        """Initialize database manager."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
        logger.info(f"Database initialized at: {self.db_path}")
    
    def get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    def init_database(self):
        """Initialize database tables."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create conversation_entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                session_id TEXT,
                user_input TEXT NOT NULL,
                assistant_response TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,  -- JSON string
                FOREIGN KEY (thread_id) REFERENCES conversations (thread_id)
            )
        """)
        
        # Create conversation_summaries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                summary_text TEXT NOT NULL,
                key_points TEXT,  -- JSON string of key points
                intent_summary TEXT,  -- Summary of user intents
                booking_info TEXT,  -- JSON string of booking information
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (thread_id) REFERENCES conversations (thread_id)
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_thread_id ON conversations (thread_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations (user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entries_thread_id ON conversation_entries (thread_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entries_user_id ON conversation_entries (user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entries_timestamp ON conversation_entries (timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_summaries_thread_id ON conversation_summaries (thread_id)")
        
        conn.commit()
        conn.close()
        logger.info("Database tables initialized successfully")
    
    def create_conversation(self, thread_id: str, user_id: str) -> bool:
        """Create a new conversation."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO conversations (thread_id, user_id, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (thread_id, user_id))
            
            conn.commit()
            conn.close()
            logger.info(f"Conversation created: {thread_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create conversation {thread_id}: {e}")
            return False
    
    def add_conversation_entry(self, thread_id: str, user_id: str, user_input: str, 
                              assistant_response: Optional[str] = None,
                              session_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add a new conversation entry."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Ensure conversation exists
            self.create_conversation(thread_id, user_id)
            
            # Add entry
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute("""
                INSERT INTO conversation_entries 
                (thread_id, user_id, session_id, user_input, assistant_response, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (thread_id, user_id, session_id, user_input, assistant_response, metadata_json))
            
            # Update conversation timestamp
            cursor.execute("""
                UPDATE conversations 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE thread_id = ?
            """, (thread_id,))
            
            conn.commit()
            conn.close()
            logger.info(f"Conversation entry added for thread {thread_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add conversation entry for thread {thread_id}: {e}")
            return False
    
    def get_conversation(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation with all entries."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get conversation info
            cursor.execute("""
                SELECT * FROM conversations WHERE thread_id = ?
            """, (thread_id,))
            
            conversation_row = cursor.fetchone()
            if not conversation_row:
                conn.close()
                return None
            
            # Get all entries
            cursor.execute("""
                SELECT * FROM conversation_entries 
                WHERE thread_id = ? 
                ORDER BY timestamp ASC
            """, (thread_id,))
            
            entries = []
            for row in cursor.fetchall():
                entry = dict(row)
                if entry['metadata']:
                    entry['metadata'] = json.loads(entry['metadata'])
                entries.append(entry)
            
            conn.close()
            
            conversation = dict(conversation_row)
            conversation['entries'] = entries
            
            return conversation
            
        except Exception as e:
            logger.error(f"Failed to get conversation {thread_id}: {e}")
            return None
    
    def get_conversation_entries(self, thread_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get conversation entries for a thread."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT * FROM conversation_entries 
                WHERE thread_id = ? 
                ORDER BY timestamp DESC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, (thread_id,))
            
            entries = []
            for row in cursor.fetchall():
                entry = dict(row)
                if entry['metadata']:
                    entry['metadata'] = json.loads(entry['metadata'])
                entries.append(entry)
            
            conn.close()
            return entries
            
        except Exception as e:
            logger.error(f"Failed to get conversation entries for {thread_id}: {e}")
            return []
    
    def list_conversations(self, user_id: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """List conversations, optionally filtered by user_id."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT c.*, 
                       COUNT(e.id) as entry_count,
                       MAX(e.timestamp) as last_message_time
                FROM conversations c
                LEFT JOIN conversation_entries e ON c.thread_id = e.thread_id
            """
            
            params = []
            if user_id:
                query += " WHERE c.user_id = ?"
                params.append(user_id)
            
            query += " GROUP BY c.thread_id ORDER BY c.updated_at DESC"
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, params)
            
            conversations = []
            for row in cursor.fetchall():
                conversation = dict(row)
                conversations.append(conversation)
            
            conn.close()
            return conversations
            
        except Exception as e:
            logger.error(f"Failed to list conversations: {e}")
            return []
    
    def get_conversation_summary(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation summary."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get conversation info with entry count
            cursor.execute("""
                SELECT c.*, 
                       COUNT(e.id) as entry_count,
                       MAX(e.timestamp) as last_message_time
                FROM conversations c
                LEFT JOIN conversation_entries e ON c.thread_id = e.thread_id
                WHERE c.thread_id = ?
                GROUP BY c.thread_id
            """, (thread_id,))
            
            conversation_row = cursor.fetchone()
            if not conversation_row:
                conn.close()
                return None
            
            # Get recent entries for summary
            cursor.execute("""
                SELECT user_input, timestamp 
                FROM conversation_entries 
                WHERE thread_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 5
            """, (thread_id,))
            
            recent_entries = []
            for row in cursor.fetchall():
                recent_entries.append({
                    'user_input': row['user_input'][:100] + "..." if len(row['user_input']) > 100 else row['user_input'],
                    'timestamp': row['timestamp']
                })
            
            conn.close()
            
            summary = dict(conversation_row)
            summary['recent_entries'] = recent_entries
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get conversation summary for {thread_id}: {e}")
            return None
    
    def save_conversation_summary(self, thread_id: str, user_id: str, summary_text: str, 
                                key_points: Optional[List[str]] = None, 
                                intent_summary: Optional[str] = None,
                                booking_info: Optional[Dict[str, Any]] = None) -> bool:
        """Save a conversation summary."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO conversation_summaries 
                (thread_id, user_id, summary_text, key_points, intent_summary, booking_info, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                thread_id, 
                user_id, 
                summary_text,
                json.dumps(key_points) if key_points else None,
                intent_summary,
                json.dumps(booking_info) if booking_info else None
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Conversation summary saved for thread {thread_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save conversation summary for {thread_id}: {e}")
            return False
    
    def get_conversation_summary_detailed(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed conversation summary including AI-generated summary."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM conversation_summaries 
                WHERE thread_id = ?
            """, (thread_id,))
            
            summary_row = cursor.fetchone()
            if not summary_row:
                conn.close()
                return None
            
            summary = dict(summary_row)
            
            # Parse JSON fields
            if summary.get('key_points'):
                summary['key_points'] = json.loads(summary['key_points'])
            if summary.get('booking_info'):
                summary['booking_info'] = json.loads(summary['booking_info'])
            
            conn.close()
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get detailed conversation summary for {thread_id}: {e}")
            return None
    
    def delete_conversation(self, thread_id: str) -> bool:
        """Delete a conversation and all its entries."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Delete entries first (due to foreign key constraint)
            cursor.execute("DELETE FROM conversation_entries WHERE thread_id = ?", (thread_id,))
            
            # Delete conversation
            cursor.execute("DELETE FROM conversations WHERE thread_id = ?", (thread_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Conversation deleted: {thread_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete conversation {thread_id}: {e}")
            return False
    
    def cleanup_old_conversations(self, days_old: int = 30) -> int:
        """Clean up conversations older than specified days."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Delete old conversations and their entries
            cursor.execute("""
                DELETE FROM conversation_entries 
                WHERE thread_id IN (
                    SELECT thread_id FROM conversations 
                    WHERE updated_at < datetime('now', '-{} days')
                )
            """.format(days_old))
            
            cursor.execute("""
                DELETE FROM conversations 
                WHERE updated_at < datetime('now', '-{} days')
            """.format(days_old))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up {deleted_count} old conversations")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old conversations: {e}")
            return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Total conversations
            cursor.execute("SELECT COUNT(*) as total_conversations FROM conversations")
            total_conversations = cursor.fetchone()['total_conversations']
            
            # Total entries
            cursor.execute("SELECT COUNT(*) as total_entries FROM conversation_entries")
            total_entries = cursor.fetchone()['total_entries']
            
            # Unique users
            cursor.execute("SELECT COUNT(DISTINCT user_id) as unique_users FROM conversations")
            unique_users = cursor.fetchone()['unique_users']
            
            # Recent activity (last 7 days)
            cursor.execute("""
                SELECT COUNT(*) as recent_entries 
                FROM conversation_entries 
                WHERE timestamp > datetime('now', '-7 days')
            """)
            recent_entries = cursor.fetchone()['recent_entries']
            
            conn.close()
            
            return {
                'total_conversations': total_conversations,
                'total_entries': total_entries,
                'unique_users': unique_users,
                'recent_entries_7_days': recent_entries
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}


# Global instance
db_manager = DatabaseManager() 