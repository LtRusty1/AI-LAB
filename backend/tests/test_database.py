import os
import sys
from datetime import datetime, timedelta
import uuid

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_lab.core.database import DatabaseManager
from ai_lab.models.base import AgentStatus, AgentRole, AgentState, AgentMetrics

@pytest.mark.asyncio
async def test_cleanup_inactive_agents_returns_removed_count(tmp_path):
    db_path = tmp_path / "test.db"
    manager = DatabaseManager(str(db_path))
    await manager.connect()

    old_agent = AgentStatus(
        id=uuid.uuid4(),
        role=AgentRole.WORKER,
        state=AgentState.IDLE,
        current_task=None,
        metrics=AgentMetrics(),
        last_updated=datetime.utcnow() - timedelta(hours=2),
    )

    active_agent = AgentStatus(
        id=uuid.uuid4(),
        role=AgentRole.WORKER,
        state=AgentState.IDLE,
        current_task=None,
        metrics=AgentMetrics(),
        last_updated=datetime.utcnow(),
    )

    await manager.update_agent_status(old_agent)
    await manager.update_agent_status(active_agent)

    removed = await manager.cleanup_inactive_agents(max_age_hours=1)
    assert removed == 1

    remaining = await manager.get_agent_status(str(active_agent.id))
    assert remaining is not None

    await manager.disconnect()
