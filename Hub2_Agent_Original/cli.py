#!/usr/bin/env python3
"""
Command-line interface for Hub2 Conversational Agent

Usage:
    python cli.py [--user-id USER_ID]
"""

import os
import sys
import argparse
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from hub2_agent.agent.orchestrator import agent


def interactive_chat(user_id: str = "user_123"):
    """Interactive chat session with the agent."""
    
    print("🤖 Hub2 Conversational Agent")
    print("=" * 50)
    print(f"👤 User ID: {user_id}")
    print("💡 Type 'quit' or 'exit' to end the session")
    print("💡 Type 'help' for example queries")
    print("=" * 50)
    
    while True:
        try:
            # Get user input
            message = input("\n💬 You: ").strip()
            
            # Check for exit commands
            if message.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            # Check for help
            if message.lower() == 'help':
                show_help()
                continue
            
            # Skip empty messages
            if not message:
                continue
            
            # Process the message
            print("🤔 Processing...")
            result = agent.process_message(user_id, message)
            
            # Display response
            print(f"\n🤖 Agent: {result['response']}")
            
            # Show function calls if any
            if result.get('function_calls'):
                print(f"\n🔧 Function calls made:")
                for i, fc in enumerate(result['function_calls'], 1):
                    print(f"   {i}. {fc['function']}({fc['arguments']})")
            
            if result.get('error'):
                print(f"\n❌ Error: {result['error']}")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def show_help():
    """Show example queries."""
    print("\n📚 Example Queries:")
    print("-" * 30)
    examples = [
        "Show me my recent transactions",
        "What are my transactions from last week?",
        "Get my transaction summary for the last 30 days",
        "Show me all completed transactions",
        "What's my transaction history for this month?",
        "How much have I spent in the last 7 days?",
        "Show me my failed transactions",
        "What's my average transaction amount?",
        "List my payment transactions",
        "Get details for transaction [TRANSACTION_ID]"
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"   {i}. {example}")


def main():
    """Main CLI function."""
    
    parser = argparse.ArgumentParser(description="Hub2 Conversational Agent CLI")
    parser.add_argument(
        "--user-id", 
        default="user_123",
        help="User ID to use for the session (default: user_123)"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run a quick test instead of interactive mode"
    )
    
    args = parser.parse_args()
    
    # Check if environment variables are set
    required_vars = ["OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables or copy env.example to .env and configure it.")
        return
    
    try:
        if args.test:
            # Run a quick test
            print("🧪 Running quick test...")
            result = agent.process_message(args.user_id, "Show me my recent transactions")
            print(f"🤖 Response: {result['response']}")
            if result.get('function_calls'):
                print(f"🔧 Function calls: {len(result['function_calls'])}")
        else:
            # Start interactive session
            interactive_chat(args.user_id)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 