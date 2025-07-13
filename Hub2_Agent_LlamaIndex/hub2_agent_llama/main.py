"""Main FastAPI application for Hub2 conversational agent with LlamaIndex."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from .api.routes import router
from . import __version__

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("🚀 Starting Hub2 Conversational Agent (LlamaIndex)...")
    logger.info(f"📦 Version: {__version__}")
    
    # Test database connection
    try:
        from .db.client import db_client
        client = db_client.get_client()
        logger.info("✅ Database connection successful")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Hub2 Conversational Agent (LlamaIndex)...")


# Create FastAPI app
app = FastAPI(
    title="Hub2 Conversational Agent (LlamaIndex)",
    description="Lightweight conversational agent for Hub2 fintech PSP-aggregator using LlamaIndex",
    version=__version__,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = time.time()
    
    # Log request
    logger.info(f"📥 {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"📤 {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)")
    
    return response


# Add exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"❌ Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if app.debug else "An unexpected error occurred"
        }
    )


# Include API routes
app.include_router(router, prefix="/api/v1", tags=["api"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Hub2 Conversational Agent (LlamaIndex)",
        "version": __version__,
        "description": "Lightweight conversational agent for Hub2 fintech PSP-aggregator using LlamaIndex",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "hub2_agent_llama.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 