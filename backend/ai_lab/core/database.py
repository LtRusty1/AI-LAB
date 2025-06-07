"""
SQLite database manager for agent state tracking and persistence.
Implements a robust state management system with proper indexing and querying.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
import sqlite3
import json
from pathlib import Path

from ..models.base import AgentStatus, AgentMetrics, AgentRole, AgentState

class DatabaseManager:
    """SQLite database manager for agent state tracking."""
    
    def __init__(self, db_path: str = "ai_lab.db"):
        self.db_path = db_path
        self._lock = asyncio.Lock()
        self._conn: Optional[sqlite3.Connection] = None
        
    async def connect(self) -> None:
        """Connect to the SQLite database and initialize tables."""
        async with self._lock:
            try:
                # Create database directory if it doesn't exist
                db_dir = Path(self.db_path).parent
                db_dir.mkdir(parents=True, exist_ok=True)
                
                # Connect to database
                self._conn = sqlite3.connect(
                    self.db_path,
                    check_same_thread=False,
                    timeout=30.0
                )
                
                # Enable foreign keys
                self._conn.execute("PRAGMA foreign_keys = ON")
                
                # Create tables
                self._create_tables()
                
            except Exception as e:
                raise ConnectionError(f"Failed to connect to database: {str(e)}")
    
    def _create_tables(self) -> None:
        """Create necessary database tables if they don't exist."""
        if not self._conn:
            raise RuntimeError("Database not connected")
        
        # Create agents table
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                role TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create agent_states table
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_states (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                state TEXT NOT NULL,
                current_task TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
            )
        """)
        
        # Create agent_metrics table
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_metrics (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                messages_processed INTEGER DEFAULT 0,
                tasks_completed INTEGER DEFAULT 0,
                errors_encountered INTEGER DEFAULT 0,
                average_response_time REAL DEFAULT 0.0,
                gpu_utilization REAL DEFAULT 0.0,
                memory_usage REAL DEFAULT 0.0,
                last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes
        self._conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_states_agent_id ON agent_states(agent_id)")
        self._conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_metrics_agent_id ON agent_metrics(agent_id)")
        
        self._conn.commit()
    
    async def disconnect(self) -> None:
        """Disconnect from the database."""
        async with self._lock:
            if self._conn:
                self._conn.close()
                self._conn = None
    
    async def update_agent_status(self, status: AgentStatus) -> None:
        """
        Update the status of an agent.
        
        Args:
            status: The new agent status
        """
        async with self._lock:
            if not self._conn:
                raise RuntimeError("Database not connected")
            
            try:
                # Update or insert agent
                self._conn.execute("""
                    INSERT OR REPLACE INTO agents (id, role, name, description, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    str(status.id),
                    status.role.value,
                    status.role.name,
                    f"{status.role.value} agent",
                    datetime.utcnow()
                ))
                
                # Update agent state
                self._conn.execute("""
                    INSERT OR REPLACE INTO agent_states
                    (id, agent_id, state, current_task, last_updated)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    f"state_{status.id}",
                    str(status.id),
                    status.state.value,
                    status.current_task,
                    status.last_updated
                ))
                
                # Update metrics
                metrics = status.metrics
                self._conn.execute("""
                    INSERT OR REPLACE INTO agent_metrics
                    (id, agent_id, messages_processed, tasks_completed,
                     errors_encountered, average_response_time, gpu_utilization,
                     memory_usage, last_heartbeat)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"metrics_{status.id}",
                    str(status.id),
                    metrics.messages_processed,
                    metrics.tasks_completed,
                    metrics.errors_encountered,
                    metrics.average_response_time,
                    metrics.gpu_utilization,
                    metrics.memory_usage,
                    metrics.last_heartbeat
                ))
                
                self._conn.commit()
                
            except Exception as e:
                self._conn.rollback()
                raise RuntimeError(f"Failed to update agent status: {str(e)}")
    
    async def get_agent_status(self, agent_id: str) -> Optional[AgentStatus]:
        """
        Get the current status of an agent.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            Optional[AgentStatus]: The agent's current status
        """
        async with self._lock:
            if not self._conn:
                raise RuntimeError("Database not connected")
            
            try:
                # Get agent info
                agent = self._conn.execute("""
                    SELECT id, role, name, description
                    FROM agents
                    WHERE id = ?
                """, (agent_id,)).fetchone()
                
                if not agent:
                    return None
                
                # Get current state
                state = self._conn.execute("""
                    SELECT state, current_task, last_updated
                    FROM agent_states
                    WHERE agent_id = ?
                """, (agent_id,)).fetchone()
                
                # Get metrics
                metrics = self._conn.execute("""
                    SELECT messages_processed, tasks_completed, errors_encountered,
                           average_response_time, gpu_utilization, memory_usage,
                           last_heartbeat
                    FROM agent_metrics
                    WHERE agent_id = ?
                """, (agent_id,)).fetchone()
                
                if not state or not metrics:
                    return None
                
                return AgentStatus(
                    id=agent[0],
                    role=AgentRole(agent[1]),
                    state=AgentState(state[0]),
                    current_task=state[1],
                    metrics=AgentMetrics(
                        messages_processed=metrics[0],
                        tasks_completed=metrics[1],
                        errors_encountered=metrics[2],
                        average_response_time=metrics[3],
                        gpu_utilization=metrics[4],
                        memory_usage=metrics[5],
                        last_heartbeat=datetime.fromisoformat(metrics[6])
                    ),
                    last_updated=datetime.fromisoformat(state[2])
                )
                
            except Exception as e:
                raise RuntimeError(f"Failed to get agent status: {str(e)}")
    
    async def get_all_agent_statuses(self) -> List[AgentStatus]:
        """
        Get the status of all agents.
        
        Returns:
            List[AgentStatus]: List of all agent statuses
        """
        async with self._lock:
            if not self._conn:
                raise RuntimeError("Database not connected")
            
            try:
                # Get all agents with their states and metrics
                results = self._conn.execute("""
                    SELECT 
                        a.id, a.role, a.name, a.description,
                        s.state, s.current_task, s.last_updated,
                        m.messages_processed, m.tasks_completed, m.errors_encountered,
                        m.average_response_time, m.gpu_utilization, m.memory_usage,
                        m.last_heartbeat
                    FROM agents a
                    LEFT JOIN agent_states s ON a.id = s.agent_id
                    LEFT JOIN agent_metrics m ON a.id = m.agent_id
                    ORDER BY a.role, a.name
                """).fetchall()
                
                statuses = []
                for row in results:
                    statuses.append(AgentStatus(
                        id=row[0],
                        role=AgentRole(row[1]),
                        state=AgentState(row[4]),
                        current_task=row[5],
                        metrics=AgentMetrics(
                            messages_processed=row[7],
                            tasks_completed=row[8],
                            errors_encountered=row[9],
                            average_response_time=row[10],
                            gpu_utilization=row[11],
                            memory_usage=row[12],
                            last_heartbeat=datetime.fromisoformat(row[13])
                        ),
                        last_updated=datetime.fromisoformat(row[6])
                    ))
                
                return statuses
                
            except Exception as e:
                raise RuntimeError(f"Failed to get agent statuses: {str(e)}")
    
    async def cleanup_inactive_agents(self, max_age_hours: int = 24) -> int:
        """
        Remove agents that have been inactive for too long.
        
        Args:
            max_age_hours: Maximum age in hours before removal
            
        Returns:
            int: Number of agents removed
        """
        async with self._lock:
            if not self._conn:
                raise RuntimeError("Database not connected")
            
            try:
                # Get inactive agents
                cutoff = datetime.utcnow().timestamp() - (max_age_hours * 3600)
                
                # Delete inactive agents (cascade will handle related records)
                self._conn.execute("""
                    DELETE FROM agents
                    WHERE id IN (
                        SELECT a.id
                        FROM agents a
                        LEFT JOIN agent_states s ON a.id = s.agent_id
                        WHERE s.last_updated < datetime(?, 'unixepoch')
                        OR s.last_updated IS NULL
                    )
                """, (cutoff,))
                
                removed = self._conn.total_changes
                self._conn.commit()
                return removed
                
            except Exception as e:
                self._conn.rollback()
                raise RuntimeError(f"Failed to cleanup inactive agents: {str(e)}") 