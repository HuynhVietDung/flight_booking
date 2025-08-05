#!/usr/bin/env python3
"""
View Conversation History
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.utils.conversation_service import conversation_service
import argparse


def view_conversations(user_id: str = None, thread_id: str = None):
    """View conversation history."""
    print("📚 Conversation History Viewer")
    print("=" * 50)
    
    if thread_id:
        # View specific conversation
        print(f"🔍 Viewing conversation: {thread_id}")
        print()
        
        conversation = conversation_service.load_conversation(thread_id)
        if conversation:
            print(f"👤 User: {conversation.user_id}")
            print(f"📅 Created: {conversation.created_at}")
            print(f"🔄 Updated: {conversation.updated_at}")
            print(f"📊 Total entries: {conversation.get_entry_count()}")
            print()
            
            print("📝 Conversation entries:")
            print("-" * 50)
            
            for i, entry in enumerate(conversation.entries, 1):
                print(f"{i:2d}. [{entry.timestamp}] {entry.user_input}")
                if entry.metadata:
                    print(f"    📋 Metadata: {entry.metadata}")
                print()
        else:
            print(f"❌ Conversation not found: {thread_id}")
    
    else:
        # List all conversations
        conversations = conversation_service.list_conversations(user_id=user_id)
        
        if not conversations:
            print("📭 No conversations found")
            if user_id:
                print(f"   (filtered by user: {user_id})")
            return
        
        print(f"📊 Found {len(conversations)} conversation(s)")
        if user_id:
            print(f"   (filtered by user: {user_id})")
        print()
        
        for i, conv in enumerate(conversations, 1):
            print(f"{i:2d}. Thread: {conv['thread_id'][:8]}...")
            print(f"    👤 User: {conv['user_id']}")
            print(f"    📊 Entries: {conv['entry_count']}")
            print(f"    📅 Created: {conv['created_at']}")
            print(f"    🔄 Updated: {conv['updated_at']}")
            # Sửa: chỉ hiển thị recent_entries nếu có
            if 'recent_entries' in conv and conv['recent_entries']:
                print("    📝 Recent messages:")
                for entry in conv['recent_entries'][:3]:
                    print(f"       - {entry['user_input']}")
            print()


def view_all_conversations(user_id: str = None):
    """View all conversations and their chat logs."""
    from src.utils.database import db_manager
    conversations = db_manager.list_conversations(user_id=user_id)
    print(f"📊 Found {len(conversations)} conversations\n")
    for i, conv in enumerate(conversations, 1):
        print(f"{i:2d}. Thread: {conv['thread_id']}")
        print(f"    👤 User: {conv['user_id']}")
        print(f"    📅 Created: {conv['created_at']}")
        print(f"    🔄 Updated: {conv['updated_at']}")
        print(f"    📊 Entries: {conv['entry_count']}")
        print("    📝 Chat log:")
        entries = db_manager.get_conversation_entries(conv['thread_id'])
        for j, entry in enumerate(reversed(entries), 1):
            print(f"      {j:2d}. [{entry['timestamp']}] {entry['user_input']}")
        print("-" * 60)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="View conversation history")
    parser.add_argument("--user", "-u", help="Filter by user ID")
    parser.add_argument("--thread", "-t", help="View specific thread ID")
    parser.add_argument("--list", "-l", action="store_true", help="List all conversations")
    
    args = parser.parse_args()
    
    if args.thread:
        view_conversations(thread_id=args.thread)
    elif args.list:
        view_conversations(user_id=args.user)
    else:
        # Nếu không có --thread và không có --list, in toàn bộ nội dung chat của tất cả các thread
        view_all_conversations(user_id=args.user)


if __name__ == "__main__":
    main() 