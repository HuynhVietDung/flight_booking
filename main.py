#!/usr/bin/env python3
"""
Main entry point for Flight Booking Agent
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.agents import EnhancedFlightAgent
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
    agent = EnhancedFlightAgent()
    
    print("🤖 Agent initialized successfully!")
    print("Type 'quit' to exit, 'help' for commands")
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
                continue
            elif user_input.lower() == 'tools':
                tools = agent.get_available_tools()
                print(f"Available tools: {', '.join(tools)}")
                continue
            elif user_input.lower() == 'config':
                settings.print_config()
                continue
            elif not user_input:
                continue
            
            print("🤖 Processing...")
            
            # Run agent
            response = agent.run(user_input)
            
            if response.success:
                print(f"🎯 Intent: {response.intent} (confidence: {response.confidence:.2f})")
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