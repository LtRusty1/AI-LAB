"""
Tests for the FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient
import types
import sys
import uuid

# Provide lightweight stubs for optional GPU dependencies so the app can be
# imported without requiring heavy libraries such as torch or cupy.
torch_stub = types.ModuleType("torch")
torch_stub.cuda = types.SimpleNamespace(
    set_device=lambda *a, **k: None,
    get_device_properties=lambda *a, **k: types.SimpleNamespace(name="stub", total_memory=1),
    empty_cache=lambda: None,
    memory_stats=lambda *a, **k: {"allocated_bytes.all.current": 0},
    set_per_process_memory_fraction=lambda *a, **k: None,
)
torch_stub.nn = types.SimpleNamespace(Module=object)
torch_stub.Tensor = object
sys.modules.setdefault("torch", torch_stub)

cupy_stub = types.ModuleType("cupy")
cupy_stub.cuda = types.SimpleNamespace(
    Device=lambda *a, **k: types.SimpleNamespace(use=lambda: None),
    MemoryPool=lambda: types.SimpleNamespace(malloc=lambda *a, **k: None, free_all_blocks=lambda: None),
    set_allocator=lambda *a, **k: None,
)
sys.modules.setdefault("cupy", cupy_stub)

numpy_stub = types.ModuleType("numpy")
sys.modules.setdefault("numpy", numpy_stub)

import ai_lab.api.app as api_app
from ai_lab.api.app import app
from ai_lab.models.base import (
    AgentMessage,
    AgentStatus,
    AgentRole,
    AgentState,
    MessageType,
)

# Ensure missing globals referenced in api_app are available during tests
api_app.AgentState = AgentState

client = TestClient(app)

def test_get_agents():
    """Test getting all agents."""
    test_agent = AgentStatus(id=uuid.uuid4(), role=AgentRole.WORKER)

    async def get_all():
        return [test_agent]

    api_app.db_manager.get_all_agent_statuses = get_all

    response = client.get("/api/agents")
    assert response.status_code == 200
    assert "agents" in response.json()

def test_get_agent():
    """Test getting a specific agent."""
    # First create a test agent
    agent_id = str(uuid.uuid4())
    agent = AgentStatus(
        id=agent_id,
        role=AgentRole.WORKER,
        state=AgentState.IDLE,
        current_task="testing",
    )

    # Mock the database response
    async def get_status(aid: str):
        return agent if aid == agent_id else None

    api_app.db_manager.get_agent_status = get_status
    
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
        sender_id=uuid.uuid4(),
        receiver_id=uuid.uuid4(),
        conversation_id=uuid.uuid4(),
        type=MessageType.TASK,
        content="Test message",
    )

    async def publish(msg: AgentMessage):
        return None

    api_app.message_broker.publish = publish

    response = client.post("/api/messages", json=message.model_dump(mode="json"))
    assert response.status_code == 200
    assert "message_id" in response.json()

def test_get_messages():
    """Test getting message history."""
    agent_id = str(uuid.uuid4())

    # Mock the message broker response
    async def history(aid: str, **kwargs):
        return []

    api_app.message_broker.get_message_history = history

    response = client.get(f"/api/messages/{agent_id}")
    assert response.status_code == 200
    assert "messages" in response.json()

def test_system_stats():
    """Test getting system statistics."""
    async def stats():
        class GPU:
            def __init__(self):
                self.total_memory = 1
                self.used_memory = 0
                self.free_memory = 1
                self.utilization = 0
                self.temperature = 0
                self.power_usage = 0
                self.timestamp = "0"

        return GPU()

    api_app.gpu_manager.get_stats = stats

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

    api_app.db_manager.get_agent_status = get_status
    api_app.db_manager.update_agent_status = update_status

    response = client.post(f"/api/agents/{agent_id}/start")
    assert response.status_code == 200
    assert response.json()["state"] == "executing"


    response = client.post(f"/api/agents/{agent_id}/stop")
    assert response.status_code == 200
    assert response.json()["state"] == "idle"

    response = client.post(f"/api/agents/{agent_id}/restart")
    assert response.status_code == 200
    assert response.json()["state"] == "executing"

