from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import chat, mcp
from models.schemas import HealthResponse
from dependencies.deps import get_notebook_service, get_mcp_client
from config.settings import settings
import logging

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI agent that connects to MCP server for notebook operations",
    version=settings.app_version,
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    **settings.cors_config
)

@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup"""
    logger.info(f"Starting {settings.app_name}...")
    
    try:
        # Initialize services
        mcp_client = get_mcp_client()
        notebook_service = get_notebook_service()
        
        logger.info(f"Connected to MCP Server: {settings.mcp_server_url}")
        logger.info(f"{settings.app_name} started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start {settings.app_name}: {e}", exc_info=True)
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info(f"Shutting down {settings.app_name}...")

# Include routers
app.include_router(chat.router)
app.include_router(mcp.router)

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint"""
    return HealthResponse(status=f"{settings.app_name} is running")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy")

# Legacy endpoint for compatibility
@app.post("/chat")
async def legacy_chat_endpoint(chat_message: dict):
    """Legacy chat endpoint for backward compatibility"""
    from models.schemas import ChatMessage
    message = ChatMessage(message=chat_message.get("message", ""))
    notebook_service = get_notebook_service()
    response = await notebook_service.process_message(message.message)
    return {"response": response}

# Legacy tools endpoint
@app.get("/tools")
async def legacy_tools_endpoint():
    """Legacy tools endpoint for backward compatibility"""
    mcp_client = get_mcp_client()
    return mcp_client.get_available_tools()

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
