#!/usr/bin/env python3
"""
Command-line interface for Hub2 LlamaIndex Agent

Usage:
    python cli_llama.py [--user-id USER_ID]
"""

import os
import sys
import argparse
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from hub2_agent_llama.agent.llama_agent import llama_agent

def interactive_chat(user_id: str = "22222222-2222-2222-2222-222222222222"):
    """Interactive chat session with the LlamaIndex agent."""
    
    print("🤖 Hub2 LlamaIndex Conversational Agent")
    print("=" * 60)
    print(f"👤 User ID: {user_id}")
    print("💡 Type 'quit' or 'exit' to end the session")
    print("💡 Type 'help' for example queries")
    print("💡 Type 'info' for agent information")
    print("=" * 60)
    
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
            
            # Check for agent info
            if message.lower() == 'info':
                show_agent_info()
                continue
            
            # Skip empty messages
            if not message:
                continue
            
            # Process the message
            print("🤔 Processing with LlamaIndex...")
            result = llama_agent.process_message(user_id, message)
            
            # Display response
            print(f"\n🤖 Agent: {result['response']}")
            
            # Show metadata if available
            if result.get('metadata'):
                print(f"\n📊 Query Info:")
                print(f"   Type: {result['metadata'].get('response_type', 'unknown')}")
                print(f"   Timestamp: {result['metadata'].get('timestamp', 'unknown')}")
            
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
    print("-" * 40)
    examples = [
        "Show me all my transactions",
        "What are my failed transactions?",
        "Get my transaction summary for the last 30 days",
        "Show me transaction tr_000001",
        "How much have I spent in total?",
        "What's my transaction history?",
        "Show me transactions from February 2025",
        "List my completed transactions",
        "What's my average transaction amount?",
        "Show me transactions with merchant M123ABC",
        "How many transactions do I have?",
        "What's my spending pattern?",
        "Show me transactions where amount > 1000 XOF",
        "List transactions ordered by date, most recent first"
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"   {i:2d}. {example}")

def show_agent_info():
    """Show agent information."""
    try:
        agent_info = llama_agent.get_agent_info()
        print("\n🤖 Agent Information:")
        print("-" * 30)
        print(f"   Type: {agent_info['agent_type']}")
        print(f"   LLM Model: {agent_info['llm_model']}")
        print(f"   Embedding Model: {agent_info['embedding_model']}")
        print(f"   Database Connected: {agent_info['database_connected']}")
        print(f"   Available Tools: {len(agent_info['available_tools'])}")
        
        for tool in agent_info['available_tools']:
            print(f"      - {tool['name']}")
            print(f"        {tool['description']}")
            
    except Exception as e:
        print(f"❌ Failed to get agent info: {e}")

def main():
    """Main CLI function."""
    
    parser = argparse.ArgumentParser(description="Hub2 LlamaIndex Conversational Agent CLI")
    parser.add_argument(
        "--user-id", 
        default="22222222-2222-2222-2222-222222222222",
        help="User ID to use for the session"
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
            print("🧪 Running quick LlamaIndex test...")
            result = llama_agent.process_message(args.user_id, "Show me my recent transactions")
            print(f"🤖 Response: {result['response']}")
            if result.get('metadata'):
                print(f"📊 Metadata: {result['metadata']}")
        else:
            # Start interactive session
            interactive_chat(args.user_id)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 