"""API routes for Hub2 agent with LlamaIndex."""

import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from .models import ChatRequest, ChatResponse, HealthResponse, AgentInfoResponse
from ..agent.llama_agent import llama_agent
from .. import __version__

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main conversational endpoint for the Hub2 LlamaIndex agent.
    
    Accepts user messages and returns agent responses with optional metadata.
    Defaults to support_team user_id if not provided.
    """
    try:
        # Use provided user_id or default to support_team
        user_id = request.user_id or "support_team"
        
        logger.info(f"Processing chat request for user: {user_id}")
        
        # Process the message through the LlamaIndex agent
        result = llama_agent.process_message(user_id, request.message)
        
        # Prepare response
        response = ChatResponse(
            response=result["response"],
            metadata=result.get("metadata") if request.include_metadata else None
        )
        
        # Add error if present
        if "error" in result:
            response.error = result["error"]
        
        logger.info(f"Chat request completed for user: {user_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=__version__,
        timestamp=datetime.now().isoformat()
    )


@router.get("/agent/info", response_model=AgentInfoResponse)
async def get_agent_info():
    """Get information about the LlamaIndex agent."""
    try:
        agent_info = llama_agent.get_agent_info()
        return AgentInfoResponse(**agent_info)
        
    except Exception as e:
        logger.error(f"Error getting agent info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "service": "Hub2 Conversational Agent (LlamaIndex)",
        "version": __version__,
        "description": "Lightweight conversational agent for Hub2 fintech PSP-aggregator using LlamaIndex",
        "endpoints": {
            "chat": "/api/v1/chat",
            "health": "/api/v1/health",
            "agent_info": "/api/v1/agent/info"
        }
    } 