"""Database migration script for Hub2 agent."""

import os
from datetime import datetime, timedelta
import random
from typing import List
from dotenv import load_dotenv

from .client import db_client
from .models import TransactionStatus, TransactionType

load_dotenv()


def create_tables():
    """Create necessary tables in Supabase."""
    client = db_client.get_client()
    
    # Create transactions table
    create_transactions_table = """
    CREATE TABLE IF NOT EXISTS transactions (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id VARCHAR(255) NOT NULL,
        amount DECIMAL(15,2) NOT NULL,
        currency VARCHAR(3) DEFAULT 'NGN',
        status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'completed', 'failed', 'cancelled')),
        type VARCHAR(20) NOT NULL CHECK (type IN ('payment', 'transfer', 'withdrawal', 'deposit', 'refund')),
        description TEXT NOT NULL,
        reference VARCHAR(255),
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    
    # Create index for faster queries
    create_indexes = """
    CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
    CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);
    CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
    """
    
    try:
        # Execute table creation
        client.rpc('exec_sql', {'sql': create_transactions_table}).execute()
        client.rpc('exec_sql', {'sql': create_indexes}).execute()
        print("✅ Tables created successfully")
    except Exception as e:
        print(f"⚠️  Table creation failed (might already exist): {e}")


def seed_dummy_data():
    """Seed database with dummy transaction data."""
    client = db_client.get_client()
    
    # Sample transaction data
    transaction_types = list(TransactionType)
    transaction_statuses = list(TransactionStatus)
    
    # Generate dummy transactions for multiple users
    users = ["user_123", "user_456", "user_789"]
    descriptions = [
        "Payment for groceries",
        "Transfer to family member",
        "ATM withdrawal",
        "Online purchase",
        "Bill payment",
        "Mobile money transfer",
        "Bank deposit",
        "Refund for cancelled order",
        "Payment for services",
        "International transfer"
    ]
    
    # Generate transactions for the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    transactions_data = []
    
    for user_id in users:
        # Generate 10-20 transactions per user
        num_transactions = random.randint(10, 20)
        
        for i in range(num_transactions):
            # Random date within the last 30 days
            days_ago = random.randint(0, 30)
            created_at = end_date - timedelta(days=days_ago)
            
            # Random amount between 1000 and 500000 NGN
            amount = round(random.uniform(1000, 500000), 2)
            
            transaction = {
                "user_id": user_id,
                "amount": amount,
                "currency": "NGN",
                "status": random.choice(transaction_statuses).value,
                "type": random.choice(transaction_types).value,
                "description": random.choice(descriptions),
                "reference": f"REF_{user_id}_{i}_{int(created_at.timestamp())}",
                "metadata": {
                    "source": random.choice(["mobile_app", "web", "atm", "pos"]),
                    "location": random.choice(["Lagos", "Abuja", "Kano", "Port Harcourt", "Kaduna"])
                },
                "created_at": created_at.isoformat(),
                "updated_at": created_at.isoformat()
            }
            transactions_data.append(transaction)
    
    # Insert transactions in batches
    batch_size = 50
    for i in range(0, len(transactions_data), batch_size):
        batch = transactions_data[i:i + batch_size]
        
        try:
            result = client.table("transactions").insert(batch).execute()
            print(f"✅ Inserted batch {i//batch_size + 1} ({len(batch)} transactions)")
        except Exception as e:
            print(f"❌ Failed to insert batch {i//batch_size + 1}: {e}")
    
    print(f"🎉 Seeded {len(transactions_data)} dummy transactions")


def main():
    """Run database migration."""
    print("🚀 Starting Hub2 database migration...")
    
    try:
        # Test database connection
        client = db_client.get_client()
        print("✅ Database connection successful")
        
        # Create tables
        create_tables()
        
        # Seed dummy data
        print("🌱 Seeding dummy data...")
        seed_dummy_data()
        
        print("🎉 Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise


if __name__ == "__main__":
    main() 