"""Compatibility wrapper for agent implementations.

This module re-exports the canonical agent classes from
``backend.ai_lab.agents`` to maintain backwards compatibility
with older imports that referenced :mod:`agents`.
"""

from typing import TypedDict, Annotated, List, Tuple

# Legacy AgentState definition used by test_setup.py
class AgentState(TypedDict):
    """Type definition for the state passed between agents."""
    message: Annotated[str, "message"]
    status: Annotated[str, "status"]
    feedback: Annotated[str, "feedback"]
    transitions: Annotated[List[Tuple[str, str]], "transitions"]

# Re-export agent implementations from backend.ai_lab.agents
from backend.ai_lab.agents import (
    CEOAgent,
    WorkerAgent,
    QAAgent,
    ReflectionAgent,
    AGENT_REGISTRY,
)

__all__ = [
    "AgentState",
    "CEOAgent",
    "WorkerAgent",
    "QAAgent",
    "ReflectionAgent",
    "AGENT_REGISTRY",
]
