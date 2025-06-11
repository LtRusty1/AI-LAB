"""
Database-aware conversation manager.
Replaces JSON file storage with PostgreSQL.
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging
from .database import db_manager

logger = logging.getLogger(__name__)

class ConversationManagerDB:
    """Database-backed conversation manager."""
    
    def __init__(self):
        self.db = db_manager
    
    async def get_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session."""
        try:
            return await self.db.get_conversation_history(session_id)
        except Exception as e:
            logger.error(f"Error loading conversation history: {str(e)}")
            return []
    
    async def add_message(self, session_id: str, role: str, content: str, thought_process: Optional[str] = None):
        """Add a message to the conversation history."""
        try:
            await self.db.add_conversation_message(session_id, role, content, thought_process)
        except Exception as e:
            logger.error(f"Error adding message to history: {str(e)}")
    
    async def get_context(self, session_id: str, max_messages: int = 5) -> str:
        """Get formatted context from recent conversation history."""
        history = await self.get_history(session_id)
        if not history:
            return ""
        
        # Get the most recent messages
        recent_messages = history[-max_messages:]
        
        # Format the context
        context = "Recent conversation history:\n\n"
        for msg in recent_messages:
            role = msg["role"]
            content = msg["content"]
            thought = msg.get("thought_process", "")
            timestamp = msg["timestamp"]
            
            context += f"[{timestamp}] {role}:\n"
            context += f"Message: {content}\n"
            if thought:
                context += f"Thought Process:\n{thought}\n"
            context += "\n"
        
        return context.strip()
    
    async def clear_history(self, session_id: str):
        """Clear conversation history for a session."""
        try:
            await self.db.clear_conversation(session_id)
        except Exception as e:
            logger.error(f"Error clearing conversation history: {str(e)}")
    
    async def save_agent_state(self, session_id: str, message: str, status: str, feedback: str, thought_process: str):
        """Save agent state to database."""
        try:
            await self.db.save_agent_state(session_id, message, status, feedback, thought_process)
        except Exception as e:
            logger.error(f"Error saving agent state: {str(e)}")
    
    async def get_agent_state(self, session_id: str) -> Optional[Dict]:
        """Get agent state from database."""
        try:
            return await self.db.get_agent_state(session_id)
        except Exception as e:
            logger.error(f"Error getting agent state: {str(e)}")
            return None 