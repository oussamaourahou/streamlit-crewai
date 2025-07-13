#!/usr/bin/env python3
"""
Debug script for Hub2 LlamaIndex Agent
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from hub2_agent_llama.agent.llama_agent import llama_agent
from hub2_agent_llama.db.client import db_client

load_dotenv()

def debug_llama_agent():
    """Debug the LlamaIndex agent setup."""
    
    print("🔍 Debugging LlamaIndex Agent")
    print("=" * 50)
    
    # 1. Check environment variables
    print("1. Checking environment variables...")
    required_vars = ["OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"   ❌ Missing: {missing_vars}")
        return False
    else:
        print("   ✅ All environment variables set")
    
    # 2. Test database connection
    print("\n2. Testing database connection...")
    try:
        client = db_client.get_client()
        result = client.table("transactions").select("count", count="exact").execute()
        print(f"   ✅ Supabase connection: {result.count} transactions")
        
        # Test connection string
        connection_string = db_client.get_connection_string()
        print(f"   🔗 PostgreSQL connection string: {connection_string[:50]}...")
        
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        return False
    
    # 3. Test LlamaIndex agent setup
    print("\n3. Testing LlamaIndex agent setup...")
    try:
        agent_info = llama_agent.get_agent_info()
        print(f"   ✅ Agent type: {agent_info['agent_type']}")
        print(f"   ✅ LLM model: {agent_info['llm_model']}")
        print(f"   ✅ Database connected: {agent_info['database_connected']}")
        print(f"   ✅ Available tools: {len(agent_info['available_tools'])}")
        
        for tool in agent_info['available_tools']:
            print(f"      - {tool['name']}: {tool['description'][:50]}...")
            
    except Exception as e:
        print(f"   ❌ Agent setup failed: {e}")
        return False
    
    # 4. Test simple query
    print("\n4. Testing simple query...")
    try:
        user_id = "22222222-2222-2222-2222-222222222222"
        result = llama_agent.process_message(user_id, "Show me my recent transactions")
        
        print(f"   ✅ Query successful")
        print(f"   📝 Response length: {len(result['response'])} characters")
        print(f"   🔧 Response preview: {result['response'][:100]}...")
        
        if result.get('metadata'):
            print(f"   📊 Metadata: {result['metadata']}")
            
    except Exception as e:
        print(f"   ❌ Query failed: {e}")
        return False
    
    print("\n✅ All tests passed! LlamaIndex agent is ready.")
    return True

def test_connection_string():
    """Test the PostgreSQL connection string generation."""
    
    print("\n🔗 Testing Connection String Generation")
    print("=" * 50)
    
    try:
        connection_string = db_client.get_connection_string()
        print(f"Generated connection string: {connection_string}")
        
        # Parse the connection string
        parts = connection_string.split("@")
        if len(parts) == 2:
            user_pass = parts[0].replace("postgresql://", "")
            host_port_db = parts[1]
            
            print(f"User/Pass: {user_pass}")
            print(f"Host/Port/DB: {host_port_db}")
            
    except Exception as e:
        print(f"❌ Connection string generation failed: {e}")

def main():
    """Main debug function."""
    
    print("🧪 Hub2 LlamaIndex Agent Debug")
    print("=" * 60)
    
    # Test connection string generation
    test_connection_string()
    
    # Test full agent setup
    success = debug_llama_agent()
    
    if success:
        print("\n🎉 LlamaIndex agent is ready for use!")
        print("\nNext steps:")
        print("1. Run: python test_llama_agent.py")
        print("2. Start API: uvicorn hub2_agent_llama.main:app --reload")
    else:
        print("\n❌ Debug failed. Please check the errors above.")

if __name__ == "__main__":
    main() 