"""API routes for Hub2 agent."""

import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from .models import (
    ChatRequest, 
    ChatResponse, 
    HealthResponse, 
    FunctionInfo, 
    FunctionsResponse
)
from ..agent.orchestrator import agent
from .. import __version__

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main conversational endpoint for the Hub2 agent.
    
    Accepts user messages and returns agent responses with optional function call details.
    """
    try:
        logger.info(f"Processing chat request for user: {request.user_id}")
        
        # Process the message through the agent
        result = agent.process_message(request.user_id, request.message)
        
        # Prepare response
        response = ChatResponse(
            response=result["response"],
            function_calls=result.get("function_calls", [])
        )
        
        # Add error if present
        if "error" in result:
            response.error = result["error"]
        
        logger.info(f"Chat request completed for user: {request.user_id}")
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


@router.get("/functions", response_model=FunctionsResponse)
async def get_functions():
    """Get available functions that the agent can call."""
    try:
        function_schemas = agent.get_available_functions()
        
        functions = []
        for schema in function_schemas:
            function_info = FunctionInfo(
                name=schema["name"],
                description=schema["description"],
                parameters=schema["parameters"]
            )
            functions.append(function_info)
        
        return FunctionsResponse(
            functions=functions,
            count=len(functions)
        )
        
    except Exception as e:
        logger.error(f"Error getting functions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "service": "Hub2 Conversational Agent",
        "version": __version__,
        "description": "Lightweight conversational agent for Hub2 fintech PSP-aggregator",
        "endpoints": {
            "chat": "/chat",
            "health": "/health", 
            "functions": "/functions"
        }
    } 