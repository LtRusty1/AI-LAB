"""
Conversation history and context management.
"""

from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ConversationManager:
    def __init__(self, history_dir: str = "conversations"):
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(exist_ok=True)
        
    def _get_conversation_file(self, session_id: str) -> Path:
        """Get the path to the conversation file for a session."""
        return self.history_dir / f"{session_id}.json"
    
    def get_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session."""
        try:
            history_file = self._get_conversation_file(session_id)
            if history_file.exists():
                with open(history_file, "r") as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error loading conversation history: {str(e)}")
            return []
    
    def add_message(self, session_id: str, role: str, content: str, thought_process: Optional[str] = None):
        """Add a message to the conversation history."""
        try:
            history = self.get_history(session_id)
            message = {
                "role": role,
                "content": content,
                "thought_process": thought_process,
                "timestamp": datetime.now().isoformat()
            }
            history.append(message)
            
            # Save updated history
            history_file = self._get_conversation_file(session_id)
            with open(history_file, "w") as f:
                json.dump(history, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error adding message to history: {str(e)}")
    
    def get_context(self, session_id: str, max_messages: int = 5) -> str:
        """Get formatted context from recent conversation history."""
        history = self.get_history(session_id)
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
    
    def clear_history(self, session_id: str):
        """Clear conversation history for a session."""
        try:
            history_file = self._get_conversation_file(session_id)
            if history_file.exists():
                history_file.unlink()
        except Exception as e:
            logger.error(f"Error clearing conversation history: {str(e)}") 