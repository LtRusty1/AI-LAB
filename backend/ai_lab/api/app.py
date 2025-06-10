"""
FastAPI application with WebSocket support for real-time agent communication.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional
import asyncio
import json
import logging
from datetime import datetime

from ..models.base import AgentMessage, AgentStatus, SystemConfig
from ..core.message_broker import MessageBroker
from ..core.database import DatabaseManager
from ..core.gpu_manager import GPUManager
from ..config.config_manager import ConfigManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections and message broadcasting."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.agent_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Connect a new WebSocket client."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client connected: {client_id}")
    
    def disconnect(self, client_id: str):
        """Disconnect a WebSocket client."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client disconnected: {client_id}")
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        for connection in self.active_connections.values():
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {str(e)}")
    
    async def send_to_agent(self, agent_id: str, message: dict):
        """Send a message to specific agent's connections."""
        if agent_id in self.agent_connections:
            for connection in self.agent_connections[agent_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to agent {agent_id}: {str(e)}")
    
    def register_agent(self, agent_id: str, websocket: WebSocket):
        """Register a WebSocket connection for an agent."""
        if agent_id not in self.agent_connections:
            self.agent_connections[agent_id] = []
        self.agent_connections[agent_id].append(websocket)
        logger.info(f"Agent registered: {agent_id}")

# Create FastAPI app
app = FastAPI(
    title="AI-Lab API",
    description="API for AI-Lab multi-agent system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your security requirements
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
config_manager = ConfigManager()
message_broker = MessageBroker(config_manager.get_config())
db_manager = DatabaseManager()
gpu_manager = GPUManager()
connection_manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    try:
        # Connect to services
        await message_broker.connect()
        await db_manager.connect()
        
        # Initialize GPU if enabled
        if config_manager.get_config().gpu.enabled:
            await gpu_manager.get_stats()  # Test GPU connection
        
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    try:
        await message_broker.disconnect()
        await db_manager.disconnect()
        logger.info("Services shut down successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time communication."""
    await connection_manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_json()
            
            # Handle different message types
            if "type" in data:
                if data["type"] == "agent_message":
                    # Forward message to message broker
                    message = AgentMessage(**data)
                    await message_broker.publish(message)
                    
                    # Broadcast to relevant clients
                    if message.receiver_id:
                        await connection_manager.send_to_agent(
                            str(message.receiver_id),
                            message.model_dump()
                        )
                    else:
                        await connection_manager.broadcast(message.model_dump())
                
                elif data["type"] == "register_agent":
                    # Register agent connection
                    agent_id = data.get("agent_id")
                    if agent_id:
                        connection_manager.register_agent(agent_id, websocket)
                        await websocket.send_json({
                            "type": "registration_confirmed",
                            "agent_id": agent_id
                        })
    
    except WebSocketDisconnect:
        connection_manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        connection_manager.disconnect(client_id)

@app.get("/api/agents")
async def get_agents():
    """Get list of all agents."""
    try:
        agents = await db_manager.get_all_agent_statuses()
        return {"agents": [agent.model_dump() for agent in agents]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get status of a specific agent."""
    try:
        agent = await db_manager.get_agent_status(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/stats")
async def get_system_stats():
    """Get system statistics including GPU usage."""
    try:
        gpu_stats = await gpu_manager.get_stats()
        return {
            "gpu": gpu_stats.__dict__,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/messages")
async def send_message(message: AgentMessage):
    """Send a message to the message broker."""
    try:
        await message_broker.publish(message)
        return {"status": "success", "message_id": str(message.id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/messages/{agent_id}")
async def get_messages(
    agent_id: str,
    limit: int = 100,
    message_types: Optional[List[str]] = None
):
    """Get message history for an agent."""
    try:
        messages = await message_broker.get_message_history(
            agent_id,
            limit=limit,
            message_types=message_types
        )
        return {"messages": [msg.model_dump() for msg in messages]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/{agent_id}/start")
async def start_agent(agent_id: str):
    """Start an agent by updating its state."""
    try:
        agent = await db_manager.get_agent_status(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        agent.state = AgentState.EXECUTING
        agent.last_updated = datetime.utcnow()
        await db_manager.update_agent_status(agent)

        # TODO: Integrate with agent pipeline to actually start processing
        return agent.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/{agent_id}/stop")
async def stop_agent(agent_id: str):
    """Stop an agent by updating its state."""
    try:
        agent = await db_manager.get_agent_status(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        agent.state = AgentState.IDLE
        agent.last_updated = datetime.utcnow()
        await db_manager.update_agent_status(agent)

        # TODO: Integrate with agent pipeline to actually stop processing
        return agent.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/{agent_id}/restart")
async def restart_agent(agent_id: str):
    """Restart an agent."""
    try:
        agent = await db_manager.get_agent_status(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        # Stop then start
        agent.state = AgentState.EXECUTING
        agent.last_updated = datetime.utcnow()
        await db_manager.update_agent_status(agent)

        # TODO: Integrate with agent pipeline for restart logic
        return agent.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
