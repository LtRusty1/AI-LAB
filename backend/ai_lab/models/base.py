"""
Base models for the AI-Lab agent system.
These models define the core data structures used throughout the system.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict

class AgentRole(str, Enum):
    """Enum defining the possible roles an agent can have."""
    CEO = "ceo"
    WORKER = "worker"
    QA = "qa"
    REFLECTION = "reflection"
    RESEARCHER = "researcher"
    PLANNER = "planner"
    EXECUTOR = "executor"

class AgentState(str, Enum):
    """Enum defining the possible states an agent can be in."""
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    WAITING = "waiting"
    ERROR = "error"
    COMPLETED = "completed"

class MessageType(str, Enum):
    """Enum defining the types of messages that can be exchanged."""
    TASK = "task"
    RESULT = "result"
    ERROR = "error"
    CONTROL = "control"
    HEARTBEAT = "heartbeat"

class BaseMessage(BaseModel):
    """Base class for all messages in the system."""
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    type: MessageType
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class AgentMessage(BaseMessage):
    """Message exchanged between agents."""
    sender_id: UUID
    receiver_id: Optional[UUID] = None
    conversation_id: UUID
    thought_process: Optional[str] = None
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class AgentConfig(BaseModel):
    """Configuration for an agent instance."""
    id: UUID = Field(default_factory=uuid4)
    role: AgentRole
    name: str
    description: str
    capabilities: List[str] = Field(default_factory=list)
    model_name: str = "mistral"
    temperature: float = 0.7
    max_tokens: int = 2000
    memory_size: int = 1000
    tools: List[str] = Field(default_factory=list)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class AgentMetrics(BaseModel):
    """Metrics for monitoring agent performance."""
    messages_processed: int = 0
    tasks_completed: int = 0
    errors_encountered: int = 0
    average_response_time: float = 0.0
    gpu_utilization: float = 0.0
    memory_usage: float = 0.0
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class AgentStatus(BaseModel):
    """Current status of an agent."""
    id: UUID
    role: AgentRole
    state: AgentState = AgentState.IDLE
    current_task: Optional[str] = None
    metrics: AgentMetrics = Field(default_factory=AgentMetrics)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class SystemConfig(BaseModel):
    """Global system configuration."""
    redis_url: str = "redis://localhost:6379"
    ollama_base_url: str = "http://localhost:11434/v1"
    database_url: str = "sqlite:///ai_lab.db"
    log_level: str = "INFO"
    max_agents: int = 100
    gpu_enabled: bool = True
    gpu_memory_limit: Optional[int] = None
    enable_monitoring: bool = True
    enable_tracing: bool = True
    
    model_config = ConfigDict(arbitrary_types_allowed=True) 