"""
Tests for the FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient
from ai_lab.api.app import app
from ai_lab.models.base import AgentMessage, AgentStatus, AgentRole, AgentState
from ai_lab.core.gpu_manager import GPUStats
import uuid

client = TestClient(app)

def test_get_agents():
    """Test getting all agents."""
    async def mock_get_all_agent_statuses():
        return []

    app.db_manager.get_all_agent_statuses = mock_get_all_agent_statuses

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
    
    # Mock the database response with async function
    async def mock_get_agent_status(aid: str):
        return agent if aid == agent_id else None

    app.db_manager.get_agent_status = mock_get_agent_status
    
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

    async def mock_publish(msg: AgentMessage):
        return None

    app.message_broker.publish = mock_publish

    response = client.post("/api/messages", json=message.model_dump())
    assert response.status_code == 200
    assert "message_id" in response.json()

def test_get_messages():
    """Test getting message history."""
    agent_id = str(uuid.uuid4())

    # Mock the message broker response
    async def mock_get_message_history(aid: str, **kwargs):
        return []

    app.message_broker.get_message_history = mock_get_message_history
    
    response = client.get(f"/api/messages/{agent_id}")
    assert response.status_code == 200
    assert "messages" in response.json()

def test_system_stats():
    """Test getting system statistics."""
    async def mock_gpu_stats():
        return GPUStats(
            total_memory=0,
            used_memory=0,
            free_memory=0,
            utilization=0.0,
            temperature=0.0,
            power_usage=0.0,
        )

    app.gpu_manager.get_stats = mock_gpu_stats

    response = client.get("/api/system/stats")
    assert response.status_code == 200
    assert "gpu" in response.json()
    assert "timestamp" in response.json()

@pytest.mark.asyncio
async def test_websocket_connection():
    """Test WebSocket connection and message handling."""
    async def mock_publish(message: AgentMessage):
        return None

    app.message_broker.publish = mock_publish

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


def test_agent_lifecycle():
    """Test start, stop and restart endpoints."""
    agent_id = str(uuid.uuid4())

    agent = AgentStatus(
        id=agent_id,
        role=AgentRole.WORKER,
        state=AgentState.IDLE,
    )

    async def get_status(aid: str):
        return agent if aid == agent_id else None

    async def update_status(status: AgentStatus):
        agent.state = status.state

    app.db_manager.get_agent_status = get_status
    app.db_manager.update_agent_status = update_status

    response = client.post(f"/api/agents/{agent_id}/start")
    assert response.status_code == 200
    assert response.json()["state"] == "executing"


    response = client.post(f"/api/agents/{agent_id}/stop")
    assert response.status_code == 200
    assert response.json()["state"] == "idle"

    response = client.post(f"/api/agents/{agent_id}/restart")
    assert response.status_code == 200
    assert response.json()["state"] == "executing"

