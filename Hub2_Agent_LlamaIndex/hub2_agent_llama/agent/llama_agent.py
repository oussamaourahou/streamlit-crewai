"""LlamaIndex-based agent for Hub2 transaction queries."""

import os
import re
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.llms.openai import OpenAI
from llama_index.core.agent import ReActAgent
from llama_index.embeddings.openai import OpenAIEmbedding

from ..db.client import db_client
from ..db.models import Transaction

logger = logging.getLogger(__name__)


class Hub2LlamaAgent:
    """Hub2 conversational agent using LlamaIndex with SQL database integration."""
    
    def __init__(self):
        self.llm = OpenAI(
            model="gpt-4o",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.embedding_model = OpenAIEmbedding(
            model="text-embedding-3-small",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize database connection
        self._setup_database()
        self._setup_agent()
    
    def _setup_database(self):
        """Setup SQL database connection and query engine."""
        try:
            # Get connection string
            connection_string = db_client.get_connection_string()
            
            # Create SQL database
            self.sql_database = SQLDatabase.from_uri(connection_string)
            
            # Create SQL query engine
            self.sql_query_engine = NLSQLTableQueryEngine(
                sql_database=self.sql_database,
                tables=["transactions"],
                llm=self.llm
            )
            
            logger.info("✅ SQL database connection established")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup SQL database: {e}")
            # Fallback to Supabase client
            self.sql_database = None
            self.sql_query_engine = None
    
    def _validate_transaction_id(self, message: str) -> Optional[str]:
        """
        Validate transaction ID format in the message.
        
        Args:
            message: User message to check for transaction IDs
            
        Returns:
            Error message if invalid transaction ID found, None if valid or no transaction ID
        """
        # Look for potential transaction ID patterns
        potential_ids = re.findall(r'\b(tr_\w+|TR_\w+|\w*tr\w*\d+|\w*TR\w*\d+)\b', message, re.IGNORECASE)
        
        if not potential_ids:
            return None
        
        # Check if any found IDs don't match the correct format
        for potential_id in potential_ids:
            if not re.match(r'^tr_[A-Za-z0-9]{6,}$', potential_id, re.IGNORECASE):
                return f"""I notice you mentioned "{potential_id}" which doesn't match our transaction ID format.

Transaction IDs in Hub2 follow this format: **tr_XXXXXXXX** (where X represents letters or numbers)

Examples of valid transaction IDs:
- tr_000001
- tr_ABC123
- tr_XYZ789

Please provide the correct transaction ID format, and I'll be happy to help you find the transaction details."""
        
        return None
    
    def _setup_agent(self):
        """Setup the ReAct agent with tools."""
        
        # Create tools
        tools = []
        
        # --- FIX: Register the SQL tool with the name 'SQL' so the agent recognizes it ---
        if self.sql_query_engine:
            sql_tool = QueryEngineTool(
                query_engine=self.sql_query_engine,
                metadata=ToolMetadata(
                    name="SQL",  # This must match what the agent expects
                    description="""Use this tool to query transaction data. 
                    The database has a 'transactions' table with columns:
                    - id (UUID)
                    - transaction_id (string, e.g., 'tr_000001')
                    - merchant_id (string)
                    - user_id (string)
                    - amount (decimal)
                    - currency (string, default 'XOF')
                    - status (string: 'pending', 'completed', 'failed', 'cancelled')
                    - date_created (timestamp)
                    - date_updated (timestamp)
                    - description (string)
                    - reference (string)
                    
                    For support team queries, you can query all transactions without user_id filters.
                    Always filter by user_id when querying for specific user data.
                    Always filter by merchant_id when querying for specific merchant data.
                    Use proper SQL syntax and be specific with WHERE clauses."""
                )
            )
            tools.append(sql_tool)
        
        # Create agent
        self.agent = ReActAgent.from_tools(
            tools,
            llm=self.llm,
            verbose=True,
            context="""You are a helpful assistant for Hub2, a fintech PSP-aggregator serving West African markets.

Your role is to help support team members with transaction queries across all users and merchants. You have access to a SQL database with transaction data.

Guidelines:
- Always be helpful and professional
- Format amounts in XOF (West African CFA Franc) with proper formatting
- When showing transaction lists, focus on the most recent transactions first
- If a user asks for "recent" transactions, default to the last 7 days
- If a user asks for "this month" or "this week", calculate the appropriate date range
- Be concise but informative in your responses
- If there are no transactions found, explain this clearly to the user
- Use transaction_id for easier reference (e.g., "tr_000123")
- Since you're serving the support team, you can query all transactions without user_id restrictions
- When querying for specific users or merchants, use the appropriate filters
- Always validate transaction ID formats before processing

Remember: You are serving West African users, so be culturally appropriate and use local context when relevant."""
        )
    
    def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """
        Process a user message and return a response.
        
        Args:
            user_id: The user ID (defaults to "support_team")
            message: The user's message
            
        Returns:
            Dictionary containing the response and metadata
        """
        try:
            # Validate transaction ID format if present
            validation_error = self._validate_transaction_id(message)
            if validation_error:
                return {
                    "response": validation_error,
                    "metadata": {
                        "user_id": user_id,
                        "query": message,
                        "response_type": "validation_error",
                        "timestamp": datetime.now().isoformat()
                    }
                }
            
            # Add context to the message based on user type
            if user_id == "support_team":
                contextual_message = f"Support Team Query: {message}"
            else:
                contextual_message = f"User ID: {user_id}\n\nUser Query: {message}"
            
            # Process with LlamaIndex agent
            response = self.agent.query(contextual_message)
            
            return {
                "response": str(response),
                "metadata": {
                    "user_id": user_id,
                    "query": message,
                    "response_type": "llama_index",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "response": "I apologize, but I encountered an error while processing your request. Please try again later.",
                "error": str(e),
                "metadata": {
                    "user_id": user_id,
                    "query": message,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the agent and available tools."""
        return {
            "agent_type": "LlamaIndex ReAct Agent",
            "llm_model": "gpt-4",
            "embedding_model": "text-embedding-3-small",
            "database_connected": self.sql_database is not None,
            "available_tools": [
                {
                    "name": "SQL",
                    "description": "SQL query engine for transaction data"
                }
            ]
        }


# Global agent instance
llama_agent = Hub2LlamaAgent() 