"""
AI-Lab agents package.
"""

from .ceo_agent import CEOAgent
from .worker_agent import WorkerAgent
from .qa_agent import QAAgent
from .reflection_agent import ReflectionAgent

# Agent registry for dynamic routing
AGENT_REGISTRY = {
    "ceo": CEOAgent,
    "worker": WorkerAgent,
    "qa": QAAgent,
    "reflection": ReflectionAgent
} 