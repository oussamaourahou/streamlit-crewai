"""Orchestrator for Hub2 conversational agent using OpenAI function calling."""

import json
import logging
from typing import List, Dict, Any, Optional
import os

import openai
from openai import OpenAI

from .functions import list_transactions, transaction_details, get_transaction_summary

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Function schemas for OpenAI function calling
FUNCTION_SCHEMAS = [
    {
        "name": "list_transactions",
        "description": "List transactions for a user, optionally within a date range",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The user ID to fetch transactions for"
                },
                "start_date": {
                    "type": "string",
                    "description": "Start date filter in YYYY-MM-DD format (optional)"
                },
                "end_date": {
                    "type": "string", 
                    "description": "End date filter in YYYY-MM-DD format (optional)"
                },
                "status": {
                    "type": "string",
                    "description": "Filter by transaction status: pending, completed, failed, cancelled (optional)"
                },
                "merchant_id": {
                    "type": "string",
                    "description": "Filter by merchant ID (optional)"
                },
                "page": {
                    "type": "integer",
                    "description": "Page number for pagination (default: 1)"
                },
                "page_size": {
                    "type": "integer",
                    "description": "Number of items per page (default: 20)"
                }
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "transaction_details",
        "description": "Get detailed information about a specific transaction",
        "parameters": {
            "type": "object",
            "properties": {
                "txn_id": {
                    "type": "string",
                    "description": "The transaction ID to fetch details for (can be transaction_id or UUID)"
                }
            },
            "required": ["txn_id"]
        }
    },
    {
        "name": "get_transaction_summary",
        "description": "Get a summary of user's transactions for a specified period",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The user ID to get summary for"
                },
                "days": {
                    "type": "integer",
                    "description": "Number of days to look back (default: 30)"
                }
            },
            "required": ["user_id"]
        }
    }
]


# Function mapping
FUNCTION_MAP = {
    "list_transactions": list_transactions,
    "transaction_details": transaction_details,
    "get_transaction_summary": get_transaction_summary
}


class Hub2Agent:
    """Hub2 conversational agent using OpenAI function calling."""
    
    def __init__(self):
        self.system_prompt = """You are a helpful assistant for Hub2, a fintech PSP-aggregator serving West African markets. 

Your role is to help users with their transaction queries. You can:
- List their transactions with optional date range filtering
- Get details about specific transactions
- Provide transaction summaries

When users ask about their transactions, use the available functions to fetch the data and then provide a helpful, natural response.

Guidelines:
- Always be helpful and professional
- Format amounts in XOF (West African CFA Franc) with proper formatting
- When showing transaction lists, focus on the most recent transactions first
- If a user asks for "recent" transactions, default to the last 7 days
- If a user asks for "this month" or "this week", calculate the appropriate date range
- Be concise but informative in your responses
- If there are no transactions found, explain this clearly to the user
- Use transaction_id for easier reference (e.g., "tr_000123")

Remember: You are serving West African users, so be culturally appropriate and use local context when relevant."""
    
    def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """
        Process a user message and return a response.
        
        Args:
            user_id: The user ID
            message: The user's message
            
        Returns:
            Dictionary containing the response and function call information
        """
        try:
            # Prepare messages for OpenAI
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"User ID: {user_id}\nMessage: {message}"}
            ]
            
            # First call to OpenAI to determine if function calling is needed
            response = client.chat.completions.create(
                model="gpt-4-0613",
                messages=messages,
                functions=FUNCTION_SCHEMAS,
                function_call="auto",
                temperature=0.1
            )
            
            response_message = response.choices[0].message
            function_calls = []
            
            # Check if function calling was triggered
            if response_message.function_call:
                function_call = response_message.function_call
                function_name = function_call.name
                function_args = json.loads(function_call.arguments)
                
                # Add user_id to function args if not present
                if function_name in ["list_transactions", "get_transaction_summary"] and "user_id" not in function_args:
                    function_args["user_id"] = user_id
                
                # Execute the function
                logger.info(f"Executing function: {function_name} with args: {function_args}")
                function_result = FUNCTION_MAP[function_name](**function_args)
                
                # Record the function call
                function_calls.append({
                    "function": function_name,
                    "arguments": function_args,
                    "result": function_result
                })
                
                # Add function call and result to messages
                messages.append(response_message)
                messages.append({
                    "role": "function",
                    "name": function_name,
                    "content": json.dumps(function_result)
                })
                
                # Second call to generate the final response
                final_response = client.chat.completions.create(
                    model="gpt-4-0613",
                    messages=messages,
                    temperature=0.1
                )
                
                final_message = final_response.choices[0].message.content
                
            else:
                # No function calling needed, use the direct response
                final_message = response_message.content
            
            return {
                "response": final_message,
                "function_calls": function_calls
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "response": "I apologize, but I encountered an error while processing your request. Please try again later.",
                "error": str(e),
                "function_calls": []
            }
    
    def get_available_functions(self) -> List[Dict]:
        """Get list of available functions and their descriptions."""
        return FUNCTION_SCHEMAS


# Global agent instance
agent = Hub2Agent() 