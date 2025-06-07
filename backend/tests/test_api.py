"""
Tests for the FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient
from ai_lab.api.app import app
from ai_lab.models.base import AgentMessage, AgentStatus
import uuid

client = TestClient(app)

def test_get_agents():
    """Test getting all agents."""
    response = client.get("/api/agents")
    assert response.status_code == 200
    assert "agents" in response.json()

def test_get_agent():
    """Test getting a specific agent."""
    # First create a test agent
    agent_id = str(uuid.uuid4())
    agent = AgentStatus(
        id=agent_id,
        name="Test Agent",
        status="active",
        capabilities=["test"],
        current_task="testing"
    )
    
    # Mock the database response
    app.db_manager.get_agent_status = lambda x: agent if x == agent_id else None
    
    # Test existing agent
    response = client.get(f"/api/agents/{agent_id}")
    assert response.status_code == 200
    assert response.json()["id"] == agent_id
    
    # Test non-existent agent
    response = client.get(f"/api/agents/{uuid.uuid4()}")
    assert response.status_code == 404

def test_send_message():
    """Test sending a message."""
    message = AgentMessage(
        sender_id=str(uuid.uuid4()),
        receiver_id=str(uuid.uuid4()),
        content="Test message",
        message_type="text"
    )
    
    response = client.post("/api/messages", json=message.model_dump())
    assert response.status_code == 200
    assert "message_id" in response.json()

def test_get_messages():
    """Test getting message history."""
    agent_id = str(uuid.uuid4())
    
    # Mock the message broker response
    app.message_broker.get_message_history = lambda x, **kwargs: []
    
    response = client.get(f"/api/messages/{agent_id}")
    assert response.status_code == 200
    assert "messages" in response.json()

def test_system_stats():
    """Test getting system statistics."""
    response = client.get("/api/system/stats")
    assert response.status_code == 200
    assert "gpu" in response.json()
    assert "timestamp" in response.json()

@pytest.mark.asyncio
async def test_websocket_connection():
    """Test WebSocket connection and message handling."""
    with client.websocket_connect("/ws/test-client") as websocket:
        # Test agent registration
        websocket.send_json({
            "type": "register_agent",
            "agent_id": "test-agent"
        })
        response = websocket.receive_json()
        assert response["type"] == "registration_confirmed"
        assert response["agent_id"] == "test-agent"
        
        # Test sending a message
        message = {
            "type": "agent_message",
            "sender_id": "test-agent",
            "content": "Test message",
            "message_type": "text"
        }
        websocket.send_json(message)
        
        # The message should be broadcast back
        response = websocket.receive_json()
        assert response["type"] == "agent_message"
        assert response["content"] == "Test message" 