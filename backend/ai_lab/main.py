from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import sys
from typing import Optional, Dict, Any
import time
from .pipeline_graph import create_agent_graph, AgentState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI-Lab Backend")

# Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent graph
graph = create_agent_graph()
compiled_graph = graph.compile()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    status: str = "success"
    error: Optional[str] = None
    thought_process: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "AI-Lab backend is running!", "status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat: ChatRequest):
    try:
        logger.info(f"Received chat request: {chat.message}")
        
        # Initialize state for the pipeline
        state = AgentState(
            message=chat.message,
            status="pending",
            feedback="",
            thought_process=""
        )
        
        # Process through the pipeline
        result = compiled_graph.invoke(state)
        
        logger.info(f"Sending response: {result['feedback']}")
        return ChatResponse(
            response=result["feedback"],
            status=result["status"],
            thought_process=result.get("thought_process", "")
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Add health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": time.time()} 