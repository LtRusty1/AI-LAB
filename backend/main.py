from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import sys
from typing import Optional, Dict
import time
from ai_lab.pipeline_graph import create_agent_graph, AgentState
from ai_lab.conversation import ConversationManager
import json
from pathlib import Path

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

# Initialize conversation manager
conversation_manager = ConversationManager()

# Initialize the agent graph with conversation manager
graph = create_agent_graph(conversation_manager=conversation_manager)
compiled_graph = graph.compile()

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

@app.get("/")
def read_root():
    return {"message": "AI-Lab backend is running!", "status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat: ChatRequest):
    try:
        logger.info(f"Received chat request: {chat.message}")
        
        # Generate session ID if not provided
        session_id = chat.session_id or str(int(time.time()))
        
        # Add user message to conversation history
        conversation_manager.add_message(
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
        
        # Save updated state
        save_state(session_id, result)
        
        # Prepare response
        response = result["feedback"]
        thought_process = result.get("thought_process", "")
        
        logger.info(f"Sending response: {response}")
        return ChatResponse(
            response=response,
            status="success",
            thought_process=thought_process,
            session_id=session_id
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversation/{session_id}")
async def get_conversation(session_id: str):
    """Get conversation history for a session."""
    try:
        history = conversation_manager.get_history(session_id)
        return {"history": history}
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/conversation/{session_id}")
async def clear_conversation(session_id: str):
    """Clear conversation history for a session."""
    try:
        conversation_manager.clear_history(session_id)
        return {"status": "success", "message": "Conversation history cleared"}
    except Exception as e:
        logger.error(f"Error clearing conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Add health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": time.time()} 