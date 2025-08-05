#!/usr/bin/env python3
"""
Main entry point for Flight Booking Agent
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.agents import FlightAgent
from src.config import settings


def main():
    """Main entry point."""
    print("🎫 Flight Booking Agent")
    print("=" * 50)
    
    # Check if .env file exists, create template if not
    if not settings.env_file.exists():
        print("📝 No .env file found. Creating template...")
        settings.create_env_template()
        print("\n⚠️  Please edit the .env file and add your OpenAI API key before running the agent.")
        print("   Then run this script again.")
        return
    
    # Validate configuration
    if not settings.validate():
        print("❌ Configuration validation failed. Please check your .env file.")
        return
    
    # Show configuration
    settings.print_config()
    
    # Create agent
    agent = FlightAgent()
    
    print("🤖 Agent initialized successfully!")
    print("Type 'quit' to exit, 'help' for commands")
    print()
    
    # Generate a unique thread_id for this session
    import uuid
    thread_id = str(uuid.uuid4())
    user_id = "demo_user"  # In a real app, this would come from authentication
    
    print(f"📝 Chat session started - Thread ID: {thread_id[:8]}...")
    print()
    
    # Interactive loop
    while True:
        try:
            user_input = input("👤 You: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'help':
                print("Available commands:")
                print("  - quit: Exit the application")
                print("  - help: Show this help")
                print("  - tools: Show available tools")
                print("  - config: Show current configuration")
                print("  - history: Info about chat history (managed by LangGraph)")
                print("  - summary: Info about session summary (managed by LangGraph)")
                print("  - stream: Enable streaming mode for next interaction")
                continue
            elif user_input.lower() == 'tools':
                tools = agent.get_available_tools()
                print(f"Available tools: {', '.join(tools)}")
                continue
            elif user_input.lower() == 'config':
                settings.print_config()
                continue
            elif user_input.lower() == 'history':
                print("📚 Chat history is now managed by LangGraph checkpointer")
                print("   Use LangGraph Studio or API to view conversation history")
                print()
                continue
            elif user_input.lower() == 'summary':
                print("📊 Session summary is now managed by LangGraph checkpointer")
                print("   Use LangGraph Studio or API to view session details")
                print()
                continue
            elif user_input.lower() == 'stream':
                print("🔄 Streaming mode enabled for next interaction")
                print("   You'll see questions streamed character by character")
                print()
                continue
            elif not user_input:
                continue
            
            print("🤖 Processing...")
            
            # Check if user wants streaming (simple heuristic: if they mentioned "stream" or "show me")
            use_streaming = any(word in user_input.lower() for word in ['stream', 'show me', 'step by step', 'progress'])
            
            if use_streaming:
                print("🔄 Streaming mode activated...")
                print()
                
                # Stream the agent execution
                current_message = ""
                for chunk in agent.stream(user_input, thread_id=thread_id, user_id=user_id):
                    # Handle custom stream data from get_stream_writer()
                    if chunk.get("type") == "question_chunk":
                        print(chunk["content"], end="", flush=True)
                        current_message += chunk["content"]
                    elif chunk.get("type") == "completion_chunk":
                        print(chunk["content"], end="", flush=True)
                        current_message += chunk["content"]
                    elif chunk.get("type") == "error":
                        print(f"❌ Error: {chunk['message']}")
                
                print("\n")
            else:
                # Run agent normally with thread_id and user_id
                response = agent.run(user_input, thread_id=thread_id, user_id=user_id)
                
                if response.success:
                    print(f"🎯 Intent: {response.intent} (confidence: {response.confidence:.2f})")
                    print(f"🌐 Language: {response.language}")
                    if response.booking_info:
                        print(f"📋 Booking Info: {response.booking_info}")
                    print(f"🤖 Agent: {response.response}")
                else:
                    print(f"❌ Error: {response.error}")
                
                print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print()


if __name__ == "__main__":
    main() 