"""Database client for Hub2 LlamaIndex agent."""

import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


class DatabaseClient:
    """Database client that supports both Supabase HTTP API and PostgreSQL direct access."""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.db_password = os.getenv("SUPABASE_DB_PASSWORD")  # Database password for PostgreSQL
        self.db_connection_string = os.getenv("SUPABASE_DB_CONNECTION_STRING")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")
    
    def get_client(self) -> Client:
        """Get Supabase client for HTTP API access."""
        return create_client(self.supabase_url, self.supabase_key)
    
    def get_connection_string(self) -> str:
        """
        Get PostgreSQL connection string for direct database access.
        Uses SUPABASE_DB_CONNECTION_STRING if set, otherwise falls back to old logic.
        """
        if self.db_connection_string:
            return self.db_connection_string
        if not self.db_password:
            raise ValueError(
                "Missing SUPABASE_DB_PASSWORD environment variable. "
                "Get this from Supabase UI: Settings > Database > Connection string"
            )
        # Extract project reference from URL
        project_ref = self.supabase_url.split("//")[1].split(".")[0]
        # Use connection pooling (recommended for better performance)
        connection_string = (
            f"postgresql://postgres.{project_ref}:{self.db_password}"
            f"@aws-0-{project_ref}.pooler.supabase.com:6543/postgres"
        )
        return connection_string
    
    def get_direct_connection_string(self) -> str:
        """
        Get direct PostgreSQL connection string (alternative to pooling).
        Use this if connection pooling doesn't work.
        """
        if self.db_connection_string:
            return self.db_connection_string
        if not self.db_password:
            raise ValueError(
                "Missing SUPABASE_DB_PASSWORD environment variable. "
                "Get this from Supabase UI: Settings > Database > Connection string"
            )
        # Extract project reference from URL
        project_ref = self.supabase_url.split("//")[1].split(".")[0]
        # Direct connection (might be blocked by firewall)
        connection_string = (
            f"postgresql://postgres:{self.db_password}"
            f"@db.{project_ref}.supabase.co:5432/postgres"
        )
        return connection_string
    
    def test_connections(self) -> dict:
        """Test both HTTP API and PostgreSQL connections."""
        results = {
            "supabase_http": False,
            "postgresql_pooling": False,
            "postgresql_direct": False
        }
        # Test Supabase HTTP API
        try:
            client = self.get_client()
            result = client.table("transactions").select("count", count="exact").execute()
            results["supabase_http"] = True
            print(f"✅ Supabase HTTP API: {result.count} transactions")
        except Exception as e:
            print(f"❌ Supabase HTTP API failed: {e}")
        # Test PostgreSQL pooling connection
        try:
            import psycopg2
            conn = psycopg2.connect(self.get_connection_string())
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM transactions;")
            count = cursor.fetchone()
            cursor.close()
            conn.close()
            results["postgresql_pooling"] = True
            print(f"✅ PostgreSQL pooling: {count[0]} transactions")
        except Exception as e:
            print(f"❌ PostgreSQL pooling failed: {e}")
        # Test PostgreSQL direct connection
        try:
            import psycopg2
            conn = psycopg2.connect(self.get_direct_connection_string())
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM transactions;")
            count = cursor.fetchone()
            cursor.close()
            conn.close()
            results["postgresql_direct"] = True
            print(f"✅ PostgreSQL direct: {count[0]} transactions")
        except Exception as e:
            print(f"❌ PostgreSQL direct failed: {e}")
        return results

# Global database client instance
db_client = DatabaseClient() 