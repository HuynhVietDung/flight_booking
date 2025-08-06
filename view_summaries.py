#!/usr/bin/env python3
"""
View Conversation Summaries
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.utils.conversation_service import conversation_service
import json


def view_summaries():
    """View all conversation summaries."""
    print("📊 Conversation Summaries")
    print("=" * 50)
    
    # Get all conversations
    conversations = conversation_service.list_conversations()
    
    if not conversations:
        print("No conversations found.")
        return
    
    print(f"Found {len(conversations)} conversations:")
    print()
    
    for i, conv in enumerate(conversations, 1):
        thread_id = conv['thread_id']
        user_id = conv['user_id']
        created_at = conv['created_at']
        
        print(f"{i}. Thread: {thread_id[:8]}... | User: {user_id} | Created: {created_at}")
        
        # Get detailed summary
        summary = conversation_service.get_conversation_summary_detailed(thread_id)
        if summary:
            print(f"   📝 Summary: {summary.get('summary_text', 'No summary')[:100]}...")
            
            booking_info = summary.get('booking_info', {})
            if booking_info:
                print(f"   📋 Booking Info: {json.dumps(booking_info, indent=2)}")
        else:
            print("   ❌ No detailed summary available")
        
        # Get conversation entries to show user/assistant messages
        entries = conversation_service.get_conversation_entries(thread_id, limit=3)
        if entries:
            print(f"   💬 Recent Messages:")
            for entry in entries[-3:]:  # Show last 3 entries
                print(f"      👤 User: {entry.get('user_input', '')[:50]}...")
                if entry.get('assistant_response'):
                    print(f"      🤖 Assistant: {entry.get('assistant_response', '')[:50]}...")
        
        print()


def view_specific_summary(thread_id: str):
    """View a specific conversation summary."""
    print(f"📊 Conversation Summary for Thread: {thread_id}")
    print("=" * 50)
    
    summary = conversation_service.get_conversation_summary_detailed(thread_id)
    if not summary:
        print("No summary found for this thread.")
        return
    
    print(f"User ID: {summary.get('user_id')}")
    print(f"Created: {summary.get('created_at')}")
    print(f"Updated: {summary.get('updated_at')}")
    print()
    
    print("📝 Summary:")
    print(summary.get('summary_text', 'No summary available'))
    print()
    
    booking_info = summary.get('booking_info', {})
    if booking_info:
        print("📋 Booking Information:")
        print(json.dumps(booking_info, indent=2))
        print()


def main():
    """Main function."""
    if len(sys.argv) > 1:
        thread_id = sys.argv[1]
        view_specific_summary(thread_id)
    else:
        view_summaries()


if __name__ == "__main__":
    main() 