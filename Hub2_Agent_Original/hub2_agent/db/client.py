"""Supabase client configuration for Hub2 agent."""

import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


class DatabaseClient:
    """Supabase client wrapper for Hub2 database operations."""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set in environment variables"
            )
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
    
    def get_client(self) -> Client:
        """Get the Supabase client instance."""
        return self.client


# Global database client instance
db_client = DatabaseClient() 