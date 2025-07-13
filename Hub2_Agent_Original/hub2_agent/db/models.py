"""Pydantic models for Hub2 transaction data."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class TransactionStatus(str, Enum):
    """Transaction status enumeration."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Transaction(BaseModel):
    """Transaction model matching your schema."""
    id: str = Field(..., description="Unique transaction ID (UUID)")
    transaction_id: str = Field(..., description="Human-readable transaction ID")
    merchant_id: str = Field(..., description="Merchant ID")
    user_id: str = Field(..., description="User ID")
    amount: float = Field(..., description="Transaction amount")
    currency: str = Field(default="XOF", description="Currency code")
    status: str = Field(..., description="Transaction status")
    date_created: str = Field(..., description="Transaction creation timestamp")
    date_updated: str = Field(..., description="Transaction last update timestamp")
    description: str = Field(..., description="Transaction description")
    reference: str = Field(..., description="External reference")


class TransactionList(BaseModel):
    """List of transactions with pagination info."""
    transactions: List[Transaction] = Field(..., description="List of transactions")
    total_count: int = Field(..., description="Total number of transactions")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")


class TransactionQuery(BaseModel):
    """Query parameters for transaction listing."""
    user_id: str = Field(..., description="User ID to filter by")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    status: Optional[str] = Field(None, description="Filter by status")
    merchant_id: Optional[str] = Field(None, description="Filter by merchant ID")
    page: int = Field(default=1, description="Page number")
    page_size: int = Field(default=20, description="Items per page") 