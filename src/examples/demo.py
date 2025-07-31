#!/usr/bin/env python3
"""
Demo script for the Flight Booking Agent
"""

import os
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from src.agents import EnhancedFlightAgent
from src.config import settings


def demo_basic_conversation():
    """Demo basic conversation flow."""
    print("🚀 Basic Conversation Demo")
    print("=" * 50)
    
    if not settings.validate():
        return
    
    agent = EnhancedFlightAgent()
    
    test_cases = [
        "Hello, I'd like to book a flight",
        "From New York to London",
        "On March 15th",
        "My name is John Smith",
        "My email is john.smith@example.com",
        "Yes, I'd like to book flight FL001"
    ]
    
    print("🤖 Agent: Hello! I'm your flight booking assistant. How can I help you today?")
    
    for i, user_input in enumerate(test_cases, 1):
        print(f"\n👤 User: {user_input}")
        
        try:
            response = agent.run(user_input)
            
            if response.success:
                print(f"🎯 Intent: {response.intent} (confidence: {response.confidence:.2f})")
                if response.booking_info:
                    print(f"📋 Collected Info: {response.booking_info}")
                print(f"🤖 Agent: {response.response}")
            else:
                print(f"❌ Error: {response.error}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print("-" * 40)


def demo_different_intents():
    """Demo different intent types."""
    print("\n🎯 Different Intents Demo")
    print("=" * 50)
    
    if not settings.validate():
        return
    
    agent = EnhancedFlightAgent()
    
    test_cases = [
        ("Flight Search", "I need to search for flights from Tokyo to Seoul on April 10th"),
        ("Weather Check", "What's the weather like in Paris?"),
        ("Flight Status", "What's the status of flight FL001?"),
        ("General Inquiry", "How much does it cost to book a flight?"),
        ("Booking Info", "I want to check my booking BKFL0011234"),
        ("Cancel Booking", "I want to cancel my booking BKFL0011234")
    ]
    
    for intent_name, user_input in test_cases:
        print(f"\n📝 {intent_name}: {user_input}")
        print("-" * 40)
        
        try:
            response = agent.run(user_input)
            
            if response.success:
                print(f"🎯 Intent: {response.intent} (confidence: {response.confidence:.2f})")
                print(f"💬 Response: {response.response}")
            else:
                print(f"❌ Error: {response.error}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print()


def demo_error_handling():
    """Demo error handling and edge cases."""
    print("\n⚠️ Error Handling Demo")
    print("=" * 50)
    
    if not settings.validate():
        return
    
    agent = EnhancedFlightAgent()
    
    edge_cases = [
        ("Empty Input", ""),
        ("Whitespace Only", "   "),
        ("Invalid Data", "Book flight from @#$% to !@#$ on date 99/99/9999"),
        ("Very Long Input", "This is a very long message that might exceed token limits " * 10),
    ]
    
    for case_name, test_input in edge_cases:
        print(f"\n🧪 {case_name}: {repr(test_input)}")
        
        try:
            response = agent.run(test_input)
            
            if response.success:
                print(f"✅ Success - Intent: {response.intent}")
                print(f"💬 Response: {response.response}")
            else:
                print(f"❌ Error handled: {response.error}")
                
        except Exception as e:
            print(f"❌ Exception: {type(e).__name__}: {e}")


def interactive_demo():
    """Interactive demo where user can chat with the agent."""
    print("\n🚀 Interactive Demo")
    print("=" * 50)
    print("Type 'quit' to exit, 'help' for commands")
    print()
    
    if not settings.validate():
        return
    
    agent = EnhancedFlightAgent()
    
    while True:
        try:
            user_input = input("🤖 You: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'help':
                print("Available commands:")
                print("  - quit: Exit the demo")
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
            
            response = agent.run(user_input)
            
            if response.success:
                print(f"🎯 Intent: {response.intent} (confidence: {response.confidence:.2f})")
                print(f"💬 Response: {response.response}")
            else:
                print(f"❌ Error: {response.error}")
            
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print()


def main():
    """Run all demos."""
    print("🎫 Flight Booking Agent - Demo")
    print("=" * 60)
    print("This demo showcases the refactored flight booking agent with:")
    print("1. Intent Classification - determines user intent with confidence")
    print("2. Collect Info - intelligently extracts and requests missing information")
    print("3. LLM Processing - handles the main booking logic with tool calling")
    print()
    
    # Check if .env file exists, create template if not
    if not settings.env_file.exists():
        print("📝 No .env file found. Creating template...")
        settings.create_env_template()
        print("\n⚠️  Please edit the .env file and add your OpenAI API key before running the demo.")
        print("   Then run this script again.")
        return
    
    # Check configuration
    if not settings.validate():
        print("❌ Configuration validation failed. Please check your .env file.")
        return
    
    # Show configuration
    settings.print_config()
    
    # Run demos
    demo_basic_conversation()
    demo_different_intents()
    demo_error_handling()
    
    # Ask if user wants interactive demo
    try:
        choice = input("\n🤔 Would you like to try the interactive demo? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            interactive_demo()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    
    print("\n✅ All demos completed!")


if __name__ == "__main__":
    main() 