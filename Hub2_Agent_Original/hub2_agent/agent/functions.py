"""Domain functions for Hub2 agent."""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

from ..db.client import db_client
from ..db.models import Transaction, TransactionList, TransactionQuery

from llama_index.core import SQLDatabase
from llama_index.core.query_engine import SQLTableQueryEngine
from llama_index.llms.openai import OpenAI

# 1. Connect to your Supabase Postgres DB
connection_string = "postgresql://USER:PASSWORD@HOST:PORT/DATABASE"
sql_database = SQLDatabase.from_uri(connection_string)

# 2. Set up LLM
llm = OpenAI(model="gpt-4", api_key="sk-...")

# 3. Create a query engine for your table
query_engine = SQLTableQueryEngine(
    sql_database=sql_database,
    tables=["transactions"],
    llm=llm,
)

# 4. Use the query engine
response = query_engine.query("List all transactions for user_id = '2222...' in February 2025")
print(response)

logger = logging.getLogger(__name__)


def list_transactions(
    user_id: str, 
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None,
    status: Optional[str] = None,
    merchant_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
) -> Dict:
    """
    Returns transactions for user_id, optionally within a date range.
    
    Args:
        user_id: The user ID to fetch transactions for
        start_date: Start date filter (YYYY-MM-DD format)
        end_date: End date filter (YYYY-MM-DD format)
        status: Filter by transaction status
        merchant_id: Filter by merchant ID
        page: Page number for pagination
        page_size: Number of items per page
    
    Returns:
        Dictionary containing transactions and metadata
    """
    try:
        client = db_client.get_client()
        
        # Build query
        query = client.table("transactions").select("*").eq("user_id", user_id)
        
        # Add date filters if provided
        if start_date:
            query = query.gte("date_created", f"{start_date}T00:00:00Z")
        if end_date:
            query = query.lte("date_created", f"{end_date}T23:59:59Z")
        
        # Add status filter if provided
        if status:
            query = query.eq("status", status)
        
        # Add merchant filter if provided
        if merchant_id:
            query = query.eq("merchant_id", merchant_id)
        
        # Add ordering and pagination
        query = query.order("date_created", desc=True)
        
        # Get total count first
        count_query = query
        count_result = count_query.execute()
        total_count = len(count_result.data)
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1)
        
        # Execute query
        result = query.execute()
        
        # Convert to Transaction objects
        transactions = []
        for row in result.data:
            try:
                transaction = Transaction(**row)
                transactions.append(transaction)
            except Exception as e:
                logger.warning(f"Failed to parse transaction {row.get('transaction_id')}: {e}")
                continue
        
        return {
            "transactions": [txn.dict() for txn in transactions],
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "has_more": (page * page_size) < total_count
        }
        
    except Exception as e:
        logger.error(f"Error fetching transactions for user {user_id}: {e}")
        return {
            "error": f"Failed to fetch transactions: {str(e)}",
            "transactions": [],
            "total_count": 0,
            "page": page,
            "page_size": page_size,
            "has_more": False
        }


def transaction_details(txn_id: str) -> Dict:
    """
    Returns full details for a specific transaction.
    
    Args:
        txn_id: The transaction ID to fetch details for (can be either id or transaction_id)
    
    Returns:
        Dictionary containing transaction details
    """
    try:
        client = db_client.get_client()
        
        # Try to find by transaction_id first, then by id
        result = client.table("transactions").select("*").eq("transaction_id", txn_id).execute()
        
        if not result.data:
            # Try by id (UUID)
            result = client.table("transactions").select("*").eq("id", txn_id).execute()
        
        if not result.data:
            return {
                "error": f"Transaction with ID {txn_id} not found"
            }
        
        # Convert to Transaction object
        transaction = Transaction(**result.data[0])
        
        return {
            "transaction": transaction.dict(),
            "found": True
        }
        
    except Exception as e:
        logger.error(f"Error fetching transaction details for {txn_id}: {e}")
        return {
            "error": f"Failed to fetch transaction details: {str(e)}",
            "found": False
        }


def get_transaction_summary(user_id: str, days: int = 30) -> Dict:
    """
    Returns a summary of user's transactions for the specified number of days.
    
    Args:
        user_id: The user ID to get summary for
        days: Number of days to look back (default: 30)
    
    Returns:
        Dictionary containing transaction summary
    """
    try:
        client = db_client.get_client()
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Query transactions in date range
        result = client.table("transactions").select("*").eq("user_id", user_id).gte(
            "date_created", start_date.isoformat()
        ).lte("date_created", end_date.isoformat()).execute()
        
        if not result.data:
            return {
                "user_id": user_id,
                "period_days": days,
                "total_transactions": 0,
                "total_amount": 0.0,
                "status_breakdown": {},
                "merchant_breakdown": {}
            }
        
        # Calculate summary statistics
        total_amount = sum(float(txn["amount"]) for txn in result.data)
        status_breakdown = {}
        merchant_breakdown = {}
        
        for txn in result.data:
            status = txn["status"]
            merchant = txn["merchant_id"]
            
            status_breakdown[status] = status_breakdown.get(status, 0) + 1
            merchant_breakdown[merchant] = merchant_breakdown.get(merchant, 0) + 1
        
        return {
            "user_id": user_id,
            "period_days": days,
            "total_transactions": len(result.data),
            "total_amount": round(total_amount, 2),
            "status_breakdown": status_breakdown,
            "merchant_breakdown": merchant_breakdown,
            "average_amount": round(total_amount / len(result.data), 2) if result.data else 0.0
        }
        
    except Exception as e:
        logger.error(f"Error fetching transaction summary for user {user_id}: {e}")
        return {
            "error": f"Failed to fetch transaction summary: {str(e)}"
        } 
    
def get_transaction_summary_by_merchant(merchant_id: str, days: int = 30) -> Dict:
    """
    Returns a summary of merchant's transactions for the specified number of days.
    
    Args:
        merchant_id: The merchant ID to get summary for
        days: Number of days to look back (default: 30)
    
    Returns:
        Dictionary containing transaction summary
    """
    try:
        client = db_client.get_client()
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Query transactions in date range
        result = client.table("transactions").select("*").eq("merchant_id", merchant_id).gte(
            "date_created", start_date.isoformat()
        ).lte("date_created", end_date.isoformat()).execute()
        
        if not result.data:
            return {
                "merchant_id": merchant_id,
                "period_days": days,
                "total_transactions": 0,
                "total_amount": 0.0,
                "status_breakdown": {},
                "user_breakdown": {}
            }
        
        # Calculate summary statistics
        total_amount = sum(float(txn["amount"]) for txn in result.data)
        status_breakdown = {}
        user_breakdown = {}
        
        for txn in result.data:
            status = txn["status"]
            merchant = txn["merchant_id"]
            
            status_breakdown[status] = status_breakdown.get(status, 0) + 1
          
        return {
            "merchant_id": merchant_id,
            "period_days": days,
            "total_transactions": len(result.data),
            "total_amount": round(total_amount, 2),
            "status_breakdown": status_breakdown,
            "user_breakdown": user_breakdown,
            "average_amount": round(total_amount / len(result.data), 2) if result.data else 0.0
        }
        
    except Exception as e:
        logger.error(f"Error fetching transaction summary for merchant {merchant_id}: {e}")
        return {
            "error": f"Failed to fetch transaction summary: {str(e)}"
        } 