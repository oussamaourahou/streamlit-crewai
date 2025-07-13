#!/usr/bin/env python3
"""
Test script for Hub2 Conversational Agent

This script demonstrates the agent's capabilities with various transaction queries.
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from hub2_agent.agent.orchestrator import agent
from hub2_agent.db.migrate import main as run_migration


def test_agent_queries():
    """Test various agent queries."""
    
    # Test user ID
    user_id = "user_123"
    
    # Test queries
    test_queries = [
        "Show me my recent transactions",
        "What are my transactions from last week?",
        "Get my transaction summary for the last 30 days",
        "Show me all completed transactions",
        "What's my transaction history for this month?",
        "Get details for transaction REF_user_123_0_1704067200",
        "How much have I spent in the last 7 days?",
        "Show me my failed transactions",
        "What's my average transaction amount?",
        "List my payment transactions"
    ]
    
    print("🤖 Hub2 Conversational Agent Test")
    print("=" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 30)
        
        try:
            # Process the query
            result = agent.process_message(user_id, query)
            
            # Display response
            print(f"💬 Response: {result['response']}")
            
            # Display function calls if any
            if result.get('function_calls'):
                print(f"🔧 Function calls: {len(result['function_calls'])}")
                for fc in result['function_calls']:
                    print(f"   - {fc['function']}: {fc['arguments']}")
            
            if result.get('error'):
                print(f"❌ Error: {result['error']}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print()


def test_direct_functions():
    """Test the domain functions directly."""
    
    print("🔧 Testing Domain Functions Directly")
    print("=" * 50)
    
    from hub2_agent.agent.functions import list_transactions, transaction_details, get_transaction_summary
    
    user_id = "user_123"
    
    # Test list_transactions
    print("\n📋 Testing list_transactions:")
    result = list_transactions(user_id, page_size=5)
    print(f"   Found {result['total_count']} transactions")
    if result['transactions']:
        print(f"   First transaction: {result['transactions'][0]['description']} - ₦{result['transactions'][0]['amount']}")
    
    # Test transaction_details (if we have a transaction ID)
    if result['transactions']:
        txn_id = result['transactions'][0]['id']
        print(f"\n🔍 Testing transaction_details for {txn_id}:")
        detail_result = transaction_details(txn_id)
        if detail_result.get('found'):
            txn = detail_result['transaction']
            print(f"   Transaction: {txn['description']} - ₦{txn['amount']} ({txn['status']})")
    
    # Test get_transaction_summary
    print("\n📊 Testing get_transaction_summary:")
    summary_result = get_transaction_summary(user_id, days=30)
    if 'error' not in summary_result:
        print(f"   Total transactions: {summary_result['total_transactions']}")
        print(f"   Total amount: ₦{summary_result['total_amount']:,.2f}")
        print(f"   Average amount: ₦{summary_result['average_amount']:,.2f}")


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
        # Run database migration first
        print("🔄 Running database migration...")
        run_migration()
        print("✅ Database migration completed")
        
        # Test direct functions
        test_direct_functions()
        
        # Test agent queries
        test_agent_queries()
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 