#!/usr/bin/env python3
"""
Test script for Hub2 LlamaIndex Agent

This script demonstrates the LlamaIndex agent's capabilities with various transaction queries.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from hub2_agent_llama.agent.llama_agent import llama_agent

load_dotenv()

def test_llama_agent_queries():
    """Test various queries with the LlamaIndex agent."""
    
    # Use the user_id from the actual data
    user_id = "22222222-2222-2222-2222-222222222222"
    
    test_queries = [
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
        "What's my spending pattern?"
    ]
    
    print("🤖 Testing Hub2 LlamaIndex Agent")
    print("=" * 60)
    print(f"👤 User ID: {user_id}")
    print(f"🕐 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    for i, query in enumerate(test_queries, 1):
        print(f"📝 Test {i:2d}: {query}")
        print("-" * 50)
        
        try:
            # Process the query
            result = llama_agent.process_message(user_id, query)
            
            # Display response
            print(f"💬 Response: {result['response']}")
            
            # Display metadata if available
            if result.get('metadata'):
                print(f"📊 Metadata: {result['metadata']}")
            
            if result.get('error'):
                print(f"❌ Error: {result['error']}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print()

def test_comparison_with_old_agent():
    """Compare LlamaIndex agent with the old function-calling agent."""
    
    print("🔄 Comparing LlamaIndex vs Function-Calling Agent")
    print("=" * 60)
    
    user_id = "22222222-2222-2222-2222-222222222222"
    test_query = "Show me my recent transactions"
    
    print(f"📝 Test Query: {test_query}")
    print(f"👤 User ID: {user_id}")
    print()
    
    # Test LlamaIndex agent
    print("🤖 LlamaIndex Agent:")
    print("-" * 30)
    try:
        llama_result = llama_agent.process_message(user_id, test_query)
        print(f"✅ Response: {llama_result['response'][:200]}...")
        print(f"📊 Response Type: {llama_result.get('metadata', {}).get('response_type', 'unknown')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test old function-calling agent (if available)
    print("🔧 Function-Calling Agent:")
    print("-" * 30)
    try:
        from hub2_agent.agent.orchestrator import agent as old_agent
        old_result = old_agent.process_message(user_id, test_query)
        print(f"✅ Response: {old_result['response'][:200]}...")
        print(f"🔧 Function Calls: {len(old_result.get('function_calls', []))}")
    except ImportError:
        print("⚠️  Old agent not available for comparison")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_agent_capabilities():
    """Test specific LlamaIndex agent capabilities."""
    
    print("🧪 Testing LlamaIndex Agent Capabilities")
    print("=" * 60)
    
    # Get agent info
    try:
        agent_info = llama_agent.get_agent_info()
        print("📋 Agent Information:")
        print(f"   Type: {agent_info['agent_type']}")
        print(f"   LLM: {agent_info['llm_model']}")
        print(f"   Embeddings: {agent_info['embedding_model']}")
        print(f"   Database Connected: {agent_info['database_connected']}")
        print(f"   Available Tools: {len(agent_info['available_tools'])}")
        
        for tool in agent_info['available_tools']:
            print(f"      - {tool['name']}")
            print(f"        {tool['description']}")
        
    except Exception as e:
        print(f"❌ Failed to get agent info: {e}")
    
    print()
    
    # Test complex queries
    complex_queries = [
        "What's the total amount of all my completed transactions?",
        "Show me transactions where the amount is greater than 1000 XOF",
        "List my transactions ordered by date, most recent first",
        "What's the breakdown of my transactions by status?",
        "Show me transactions from the last 7 days with amounts between 500 and 2000 XOF"
    ]
    
    user_id = "22222222-2222-2222-2222-222222222222"
    
    for i, query in enumerate(complex_queries, 1):
        print(f"🔍 Complex Query {i}: {query}")
        print("-" * 40)
        
        try:
            result = llama_agent.process_message(user_id, query)
            print(f"💬 Response: {result['response'][:150]}...")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

def main():
    """Main test function."""
    
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
        # Test basic queries
        test_llama_agent_queries()
        
        # Test agent capabilities
        test_agent_capabilities()
        
        # Test comparison
        test_comparison_with_old_agent()
        
        print("\n🎉 All LlamaIndex tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 