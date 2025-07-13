"""API models for Hub2 agent with LlamaIndex."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    user_id: Optional[str] = Field(default="support_team", description="User ID (defaults to support_team)")
    message: str = Field(..., description="User message")
    include_metadata: bool = Field(default=False, description="Include query metadata in response")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="Agent response")
    metadata: Optional[dict] = Field(None, description="Query metadata")
    error: Optional[str] = Field(None, description="Error message if any")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")


class ToolInfo(BaseModel):
    """Model for tool information."""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")


class AgentInfoResponse(BaseModel):
    """Response model for agent info endpoint."""
    agent_type: str = Field(..., description="Type of agent")
    llm_model: str = Field(..., description="LLM model being used")
    embedding_model: str = Field(..., description="Embedding model being used")
    database_connected: bool = Field(..., description="Whether database is connected")
    available_tools: List[ToolInfo] = Field(..., description="Available tools") 