#!/usr/bin/env python3
"""
Script to inspect SQLite database contents
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime


def inspect_checkpoint_db(db_path: str = "data/langgraph_checkpoints.db"):
    """Inspect LangGraph checkpoint database."""
    print("🔍 Inspecting LangGraph Checkpoint Database")
    print("=" * 50)
    
    if not Path(db_path).exists():
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📋 Tables found: {[table[0] for table in tables]}")
        print()
        
        # Inspect each table
        for table in tables:
            table_name = table[0]
            print(f"📊 Table: {table_name}")
            print("-" * 30)
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            print("Columns:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"Row count: {count}")
            
            # Show sample data
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                rows = cursor.fetchall()
                print("Sample data:")
                for i, row in enumerate(rows, 1):
                    print(f"  Row {i}: {row}")
            
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error inspecting database: {e}")


def inspect_checkpoints_detailed(db_path: str = "data/langgraph_checkpoints.db"):
    """Detailed inspection of checkpoints."""
    print("🔍 Detailed Checkpoint Inspection")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all checkpoints
        cursor.execute("""
            SELECT thread_id, checkpoint_id, parent_checkpoint_id, 
                   created_at, metadata, values, next
            FROM checkpoints 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        
        checkpoints = cursor.fetchall()
        
        if not checkpoints:
            print("No checkpoints found.")
            return
        
        print(f"Found {len(checkpoints)} recent checkpoints:")
        print()
        
        for i, checkpoint in enumerate(checkpoints, 1):
            thread_id, checkpoint_id, parent_id, created_at, metadata, values, next_nodes = checkpoint
            
            print(f"🔹 Checkpoint {i}")
            print(f"   Thread ID: {thread_id}")
            print(f"   Checkpoint ID: {checkpoint_id[:8]}...")
            print(f"   Parent: {parent_id[:8] if parent_id else 'None'}...")
            print(f"   Created: {created_at}")
            
            # Parse metadata
            if metadata:
                try:
                    meta = json.loads(metadata)
                    print(f"   Metadata: {meta}")
                except:
                    print(f"   Metadata: {metadata}")
            
            # Parse values (state)
            if values:
                try:
                    state_values = json.loads(values)
                    print(f"   State keys: {list(state_values.keys())}")
                    
                    # Show messages if available
                    if 'messages' in state_values:
                        messages = state_values['messages']
                        print(f"   Messages: {len(messages)} messages")
                        for j, msg in enumerate(messages[-2:], 1):  # Show last 2
                            if hasattr(msg, 'content'):
                                content = msg.content[:100] + "..." if len(str(msg.content)) > 100 else str(msg.content)
                                print(f"     Message {j}: {content}")
                    
                    # Show intent classification if available
                    if 'intent_classification' in state_values:
                        intent = state_values['intent_classification']
                        print(f"   Intent: {intent.get('intent', 'N/A')} (confidence: {intent.get('confidence', 'N/A')})")
                    
                    # Show booking info if available
                    if 'booking_info' in state_values:
                        booking = state_values['booking_info']
                        print(f"   Booking info: {booking}")
                        
                except Exception as e:
                    print(f"   Values: Error parsing - {e}")
            
            # Parse next nodes
            if next_nodes:
                try:
                    next_list = json.loads(next_nodes)
                    print(f"   Next nodes: {next_list}")
                except:
                    print(f"   Next nodes: {next_nodes}")
            
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error in detailed inspection: {e}")


def inspect_threads(db_path: str = "data/langgraph_checkpoints.db"):
    """Inspect threads and their checkpoints."""
    print("🧵 Thread Inspection")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get unique threads
        cursor.execute("SELECT DISTINCT thread_id FROM checkpoints ORDER BY thread_id;")
        threads = cursor.fetchall()
        
        if not threads:
            print("No threads found.")
            return
        
        print(f"Found {len(threads)} threads:")
        print()
        
        for thread in threads:
            thread_id = thread[0]
            
            # Get checkpoint count for this thread
            cursor.execute("SELECT COUNT(*) FROM checkpoints WHERE thread_id = ?", (thread_id,))
            count = cursor.fetchone()[0]
            
            # Get first and last checkpoint
            cursor.execute("""
                SELECT created_at FROM checkpoints 
                WHERE thread_id = ? 
                ORDER BY created_at ASC 
                LIMIT 1
            """, (thread_id,))
            first = cursor.fetchone()
            
            cursor.execute("""
                SELECT created_at FROM checkpoints 
                WHERE thread_id = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            """, (thread_id,))
            last = cursor.fetchone()
            
            print(f"🔹 Thread: {thread_id[:8]}...")
            print(f"   Checkpoints: {count}")
            print(f"   First: {first[0] if first else 'N/A'}")
            print(f"   Last: {last[0] if last else 'N/A'}")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error inspecting threads: {e}")


def search_checkpoints(query: str, db_path: str = "data/langgraph_checkpoints.db"):
    """Search checkpoints by content."""
    print(f"🔍 Searching checkpoints for: '{query}'")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Search in values (state content)
        cursor.execute("""
            SELECT thread_id, checkpoint_id, created_at, values
            FROM checkpoints 
            WHERE values LIKE ?
            ORDER BY created_at DESC 
            LIMIT 5
        """, (f"%{query}%",))
        
        results = cursor.fetchall()
        
        if not results:
            print("No results found.")
            return
        
        print(f"Found {len(results)} matching checkpoints:")
        print()
        
        for i, result in enumerate(results, 1):
            thread_id, checkpoint_id, created_at, values = result
            
            print(f"🔹 Result {i}")
            print(f"   Thread: {thread_id[:8]}...")
            print(f"   Checkpoint: {checkpoint_id[:8]}...")
            print(f"   Created: {created_at}")
            
            # Show matching content
            try:
                state_values = json.loads(values)
                if 'messages' in state_values:
                    messages = state_values['messages']
                    for j, msg in enumerate(messages):
                        if hasattr(msg, 'content') and query.lower() in str(msg.content).lower():
                            content = str(msg.content)[:200] + "..." if len(str(msg.content)) > 200 else str(msg.content)
                            print(f"   Match: {content}")
                            break
            except:
                pass
            
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error searching: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "basic":
            inspect_checkpoint_db()
        elif command == "detailed":
            inspect_checkpoints_detailed()
        elif command == "threads":
            inspect_threads()
        elif command == "search" and len(sys.argv) > 2:
            search_checkpoints(sys.argv[2])
        else:
            print("Usage:")
            print("  python inspect_db.py basic      - Basic table inspection")
            print("  python inspect_db.py detailed   - Detailed checkpoint inspection")
            print("  python inspect_db.py threads    - Thread inspection")
            print("  python inspect_db.py search <query> - Search checkpoints")
    else:
        # Run all inspections
        inspect_checkpoint_db()
        print("\n" + "="*60 + "\n")
        inspect_checkpoints_detailed()
        print("\n" + "="*60 + "\n")
        inspect_threads() 