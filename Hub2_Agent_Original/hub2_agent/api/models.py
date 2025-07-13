"""API models for Hub2 agent."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    user_id: str = Field(..., description="User ID")
    message: str = Field(..., description="User message")
    include_function_calls: bool = Field(default=False, description="Include function call details in response")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="Agent response")
    function_calls: List[Dict[str, Any]] = Field(default_factory=list, description="Function calls made")
    error: Optional[str] = Field(None, description="Error message if any")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")


class FunctionInfo(BaseModel):
    """Model for function information."""
    name: str = Field(..., description="Function name")
    description: str = Field(..., description="Function description")
    parameters: Dict[str, Any] = Field(..., description="Function parameters schema")


class FunctionsResponse(BaseModel):
    """Response model for functions endpoint."""
    functions: List[FunctionInfo] = Field(..., description="Available functions")
    count: int = Field(..., description="Number of available functions") 