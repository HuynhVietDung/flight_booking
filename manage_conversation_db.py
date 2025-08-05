#!/usr/bin/env python3
"""
Manage Conversation Database
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.utils.database import db_manager
from src.utils.conversation_service import conversation_service
import argparse
import json


def show_statistics():
    """Show database statistics."""
    print("📊 Database Statistics")
    print("=" * 50)
    
    stats = db_manager.get_statistics()
    
    print(f"📈 Total conversations: {stats['total_conversations']}")
    print(f"💬 Total entries: {stats['total_entries']}")
    print(f"👥 Unique users: {stats['unique_users']}")
    print(f"🕒 Recent entries (7 days): {stats['recent_entries_7_days']}")
    
    if stats['total_conversations'] > 0:
        avg_entries = stats['total_entries'] / stats['total_conversations']
        print(f"📊 Average entries per conversation: {avg_entries:.1f}")


def list_conversations(user_id=None, limit=None):
    """List conversations."""
    print("📚 Conversations")
    print("=" * 50)
    
    conversations = db_manager.list_conversations(user_id=user_id, limit=limit)
    
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
        
        if conv.get('last_message_time'):
            print(f"    💬 Last message: {conv['last_message_time']}")
        
        print()


def show_conversation(thread_id):
    """Show detailed conversation."""
    print(f"🔍 Conversation: {thread_id}")
    print("=" * 50)
    
    conversation = db_manager.get_conversation(thread_id)
    if not conversation:
        print(f"❌ Conversation not found: {thread_id}")
        return
    
    print(f"👤 User: {conversation['user_id']}")
    print(f"📅 Created: {conversation['created_at']}")
    print(f"🔄 Updated: {conversation['updated_at']}")
    print(f"📊 Total entries: {len(conversation['entries'])}")
    print()
    
    print("📝 Conversation entries:")
    print("-" * 50)
    
    for i, entry in enumerate(conversation['entries'], 1):
        print(f"{i:2d}. [{entry['timestamp']}] {entry['user_input']}")
        if entry.get('metadata'):
            print(f"    📋 Metadata: {json.dumps(entry['metadata'], indent=2)}")
        print()


def delete_conversation(thread_id):
    """Delete a conversation."""
    print(f"🗑️  Deleting conversation: {thread_id}")
    print("=" * 50)
    
    # Show conversation first
    conversation = db_manager.get_conversation(thread_id)
    if not conversation:
        print(f"❌ Conversation not found: {thread_id}")
        return
    
    print(f"👤 User: {conversation['user_id']}")
    print(f"📊 Entries: {len(conversation['entries'])}")
    print(f"📅 Created: {conversation['created_at']}")
    print()
    
    # Confirm deletion
    confirm = input("⚠️  Are you sure you want to delete this conversation? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Deletion cancelled")
        return
    
    # Delete conversation
    success = db_manager.delete_conversation(thread_id)
    if success:
        print("✅ Conversation deleted successfully")
    else:
        print("❌ Failed to delete conversation")


def cleanup_old_conversations(days):
    """Clean up old conversations."""
    print(f"🧹 Cleaning up conversations older than {days} days")
    print("=" * 50)
    
    # Show what will be deleted
    conversations = db_manager.list_conversations()
    print(f"📊 Total conversations before cleanup: {len(conversations)}")
    
    # Perform cleanup
    deleted_count = db_manager.cleanup_old_conversations(days)
    
    print(f"🗑️  Deleted {deleted_count} old conversations")
    
    # Show remaining
    remaining = db_manager.list_conversations()
    print(f"📊 Remaining conversations: {len(remaining)}")


def export_conversation(thread_id, output_file):
    """Export conversation to JSON file."""
    print(f"📤 Exporting conversation: {thread_id}")
    print("=" * 50)
    
    conversation = db_manager.get_conversation(thread_id)
    if not conversation:
        print(f"❌ Conversation not found: {thread_id}")
        return
    
    # Prepare export data
    export_data = {
        'thread_id': conversation['thread_id'],
        'user_id': conversation['user_id'],
        'created_at': conversation['created_at'],
        'updated_at': conversation['updated_at'],
        'entries': conversation['entries']
    }
    
    # Write to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✅ Conversation exported to: {output_file}")
        print(f"📊 Exported {len(conversation['entries'])} entries")
        
    except Exception as e:
        print(f"❌ Failed to export conversation: {e}")


def search_conversations(query, user_id=None):
    """Search conversations by content."""
    print(f"🔍 Searching conversations for: '{query}'")
    print("=" * 50)
    
    # Get all conversations
    conversations = db_manager.list_conversations(user_id=user_id)
    
    results = []
    for conv in conversations:
        # Get entries for this conversation
        entries = db_manager.get_conversation_entries(conv['thread_id'])
        
        # Search in entries
        for entry in entries:
            if query.lower() in entry['user_input'].lower():
                results.append({
                    'thread_id': conv['thread_id'],
                    'user_id': conv['user_id'],
                    'entry': entry,
                    'conversation': conv
                })
    
    if not results:
        print("📭 No matching conversations found")
        return
    
    print(f"📊 Found {len(results)} matching entries")
    print()
    
    for i, result in enumerate(results[:10], 1):  # Show first 10 results
        print(f"{i:2d}. Thread: {result['thread_id'][:8]}...")
        print(f"    👤 User: {result['user_id']}")
        print(f"    📅 Time: {result['entry']['timestamp']}")
        print(f"    💬 Message: {result['entry']['user_input']}")
        print()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Manage Conversation Database")
    parser.add_argument("command", choices=[
        "stats", "list", "show", "delete", "cleanup", "export", "search"
    ], help="Command to execute")
    
    parser.add_argument("--user", "-u", help="Filter by user ID")
    parser.add_argument("--thread", "-t", help="Thread ID")
    parser.add_argument("--limit", "-l", type=int, help="Limit number of results")
    parser.add_argument("--days", "-d", type=int, default=30, help="Days for cleanup")
    parser.add_argument("--output", "-o", help="Output file for export")
    parser.add_argument("--query", "-q", help="Search query")
    
    args = parser.parse_args()
    
    if args.command == "stats":
        show_statistics()
    
    elif args.command == "list":
        list_conversations(user_id=args.user, limit=args.limit)
    
    elif args.command == "show":
        if not args.thread:
            print("❌ Thread ID required for show command")
            return
        show_conversation(args.thread)
    
    elif args.command == "delete":
        if not args.thread:
            print("❌ Thread ID required for delete command")
            return
        delete_conversation(args.thread)
    
    elif args.command == "cleanup":
        cleanup_old_conversations(args.days)
    
    elif args.command == "export":
        if not args.thread:
            print("❌ Thread ID required for export command")
            return
        if not args.output:
            args.output = f"conversation_{args.thread[:8]}.json"
        export_conversation(args.thread, args.output)
    
    elif args.command == "search":
        if not args.query:
            print("❌ Search query required for search command")
            return
        search_conversations(args.query, user_id=args.user)


if __name__ == "__main__":
    main() 