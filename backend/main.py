from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
import logging
import sys
from typing import Optional, Dict, List
import time
from ai_lab.pipeline_graph import create_agent_graph, AgentState
from ai_lab.conversation_db import ConversationManagerDB
from ai_lab.database import db_manager
from ai_lab.performance import performance_monitor, monitor_performance
from ai_lab.api_keys import api_key_manager
import json
from pathlib import Path
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI-Lab Backend", version="2.0.0")

# Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database-backed conversation manager
conversation_manager = ConversationManagerDB()

# Initialize the agent graph with conversation manager
pipeline_graph = create_agent_graph(conversation_manager=conversation_manager)
compiled_graph = pipeline_graph.graph.compile()

# State management
STATE_DIR = Path("states")
STATE_DIR.mkdir(exist_ok=True)

def load_state(session_id: str) -> Dict:
    """Load state for a session."""
    state_file = STATE_DIR / f"{session_id}.json"
    if state_file.exists():
        with open(state_file, "r") as f:
            return json.load(f)
    return {
        "message": "",
        "status": "pending",
        "feedback": "",
        "thought_process": ""
    }

def save_state(session_id: str, state: Dict):
    """Save state for a session."""
    state_file = STATE_DIR / f"{session_id}.json"
    with open(state_file, "w") as f:
        json.dump(state, f)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    status: str = "success"
    error: Optional[str] = None
    thought_process: Optional[str] = None
    session_id: Optional[str] = None

class APIKeyRequest(BaseModel):
    service_name: str
    api_key: str

class APIKeyResponse(BaseModel):
    success: bool
    message: str
    service_name: str

# Startup event to initialize database
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    try:
        await db_manager.create_tables()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

@app.get("/")
def read_root():
    return {"message": "AI-Lab backend v2.0 is running!", "status": "healthy", "features": ["database", "performance_monitoring", "api_key_management"]}

@app.post("/chat", response_model=ChatResponse)
@monitor_performance("chat_endpoint")
async def chat_endpoint(chat: ChatRequest):
    try:
        logger.info(f"Received chat request: {chat.message}")
        
        # Generate session ID if not provided
        session_id = chat.session_id or str(int(time.time()))
        
        # Add user message to conversation history (database)
        await conversation_manager.add_message(
            session_id,
            "User",
            chat.message
        )
        
        # Initialize state with session ID
        state = AgentState(
            message=chat.message,
            status="pending",
            feedback="",
            thought_process="",
            session_id=session_id
        )
        
        # Process through agent pipeline
        result = compiled_graph.invoke(state)
        
        # Handle LangGraph return value (could be AddableValuesDict)
        if hasattr(result, '__dict__'):
            # If it's an object with attributes, convert to our AgentState
            if hasattr(result, 'message'):
                result_state = result
            else:
                # If it doesn't have the expected attributes, check the dict values
                result_dict = dict(result) if hasattr(result, 'keys') else {}
                result_state = AgentState.from_dict(result_dict)
        elif isinstance(result, dict):
            # If it's a dictionary, convert to AgentState
            result_state = AgentState.from_dict(result)
        else:
            # Fallback for unexpected types
            result_state = AgentState(
                message=chat.message,
                status="error", 
                feedback="Unexpected result type from agent pipeline",
                thought_process="Error: Pipeline returned unexpected type",
                session_id=session_id
            )
        
        # Save agent state to database
        await conversation_manager.save_agent_state(
            session_id,
            result_state.message,
            result_state.status,
            result_state.feedback,
            result_state.thought_process
        )
        
        # Add assistant response to conversation history
        await conversation_manager.add_message(
            session_id,
            "Assistant",
            result_state.feedback,
            result_state.thought_process
        )
        
        # Prepare response
        response = result_state.feedback
        thought_process = result_state.thought_process
        
        logger.info(f"Sending response: {response}")
        return ChatResponse(
            response=response,
            status="success",
            thought_process=thought_process,
            session_id=session_id
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        return ChatResponse(
            response="Sorry, there was an error processing your request. Please try again.",
            status="error",
            error=str(e),
            session_id=session_id if 'session_id' in locals() else None
        )

@app.get("/conversation/{session_id}")
async def get_conversation(session_id: str):
    """Get conversation history for a session."""
    try:
        history = await conversation_manager.get_history(session_id)
        return {"history": history}
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/conversation/{session_id}")
async def clear_conversation(session_id: str):
    """Clear conversation history for a session."""
    try:
        await conversation_manager.clear_history(session_id)
        return {"status": "success", "message": "Conversation history cleared"}
    except Exception as e:
        logger.error(f"Error clearing conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# API Key Management Endpoints
@app.post("/api-keys", response_model=APIKeyResponse)
async def store_api_key(request: APIKeyRequest):
    """Store an API key for a service."""
    try:
        # Validate API key format
        if not await api_key_manager.validate_api_key_format(request.service_name, request.api_key):
            return APIKeyResponse(
                success=False,
                message="Invalid API key format",
                service_name=request.service_name
            )
        
        success = await api_key_manager.store_api_key(request.service_name, request.api_key)
        
        return APIKeyResponse(
            success=success,
            message="API key stored successfully" if success else "Failed to store API key",
            service_name=request.service_name
        )
    except Exception as e:
        logger.error(f"Error storing API key: {e}")
        return APIKeyResponse(
            success=False,
            message=f"Error: {str(e)}",
            service_name=request.service_name
        )

@app.get("/api-keys")
async def list_api_keys():
    """List configured API key services."""
    try:
        services = await api_key_manager.list_configured_services()
        supported = api_key_manager.get_supported_services()
        
        return {
            "configured_services": services,
            "supported_services": supported
        }
    except Exception as e:
        logger.error(f"Error listing API keys: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api-keys/{service_name}/test")
async def test_api_key(service_name: str, request: APIKeyRequest):
    """Test if an API key is valid."""
    try:
        result = await api_key_manager.test_api_key(service_name, request.api_key)
        return result
    except Exception as e:
        logger.error(f"Error testing API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api-keys/{service_name}")
async def remove_api_key(service_name: str):
    """Remove an API key for a service."""
    try:
        success = await api_key_manager.remove_api_key(service_name)
        return {
            "success": success,
            "message": "API key removed successfully" if success else "Failed to remove API key"
        }
    except Exception as e:
        logger.error(f"Error removing API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Performance Monitoring Endpoints
@app.get("/metrics")
async def get_metrics():
    """Get current system metrics."""
    try:
        return await performance_monitor.collect_system_metrics()
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/prometheus")
async def get_prometheus_metrics():
    """Get Prometheus-formatted metrics."""
    try:
        metrics = performance_monitor.get_prometheus_metrics()
        return PlainTextResponse(metrics, media_type="text/plain")
    except Exception as e:
        logger.error(f"Error getting Prometheus metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/performance/summary")
async def get_performance_summary(hours: int = 24):
    """Get performance summary for the last N hours."""
    try:
        return await performance_monitor.get_performance_summary(hours)
    except Exception as e:
        logger.error(f"Error getting performance summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/benchmark/llm")
async def benchmark_llm(model_name: str = "default", prompt: str = "Hello, world!", iterations: int = 5):
    """Benchmark LLM inference performance."""
    try:
        return await performance_monitor.benchmark_llm_inference(model_name, prompt, iterations)
    except Exception as e:
        logger.error(f"Error running LLM benchmark: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced health check endpoint
@app.get("/health")
async def health_check():
    """Health check with system information."""
    try:
        metrics = await performance_monitor.collect_system_metrics()
        return {
            "status": "healthy", 
            "timestamp": time.time(),
            "database": "connected",
            "metrics": metrics
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": time.time(),
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting AI-Lab backend server v2.0 with enhanced features...")
    uvicorn.run(app, host="127.0.0.1", port=8001)