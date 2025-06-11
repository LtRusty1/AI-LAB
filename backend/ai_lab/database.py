"""
Database models and configuration for AI-Lab.
Migrates from JSON file storage to PostgreSQL.
"""

from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Boolean, LargeBinary, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional, List, Dict
import os
import json
import logging
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, index=True)
    role = Column(String)  # user, assistant, system
    content = Column(Text)
    thought_process = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
class AgentState(Base):
    __tablename__ = "agent_states"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    message = Column(Text)
    status = Column(String)  # pending, complete, error
    feedback = Column(Text)
    thought_process = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String, unique=True, index=True)  # openai, anthropic, etc.
    encrypted_key = Column(LargeBinary)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, index=True)
    metric_value = Column(String)
    session_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv(
            "DATABASE_URL", 
            "postgresql+asyncpg://postgres:password@localhost:5432/ai_lab"
        )
        self.engine = create_async_engine(self.database_url)
        self.SessionLocal = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=self.engine,
            class_=AsyncSession
        )
        
        # Initialize encryption key for API keys
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for API keys."""
        key_file = "encryption_key.key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            return key
    
    async def create_tables(self):
        """Create all tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def get_session(self):
        """Get database session."""
        async with self.SessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()
    
    # Conversation methods
    async def add_conversation_message(
        self, 
        session_id: str, 
        role: str, 
        content: str, 
        thought_process: Optional[str] = None
    ):
        """Add a message to conversation history."""
        async with self.SessionLocal() as session:
            message = Conversation(
                id=f"{session_id}_{datetime.utcnow().timestamp()}",
                session_id=session_id,
                role=role,
                content=content,
                thought_process=thought_process
            )
            session.add(message)
            await session.commit()
    
    async def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session."""
        async with self.SessionLocal() as session:
            result = await session.execute(
                text("SELECT * FROM conversations WHERE session_id = :session_id ORDER BY timestamp"),
                {"session_id": session_id}
            )
            conversations = result.fetchall()
            return [
                {
                    "role": conv.role,
                    "content": conv.content,
                    "thought_process": conv.thought_process,
                    "timestamp": conv.timestamp.isoformat()
                }
                for conv in conversations
            ]
    
    async def clear_conversation(self, session_id: str):
        """Clear conversation history for a session."""
        async with self.SessionLocal() as session:
            await session.execute(
                text("DELETE FROM conversations WHERE session_id = :session_id"),
                {"session_id": session_id}
            )
            await session.commit()
    
    # Agent state methods
    async def save_agent_state(
        self,
        session_id: str,
        message: str,
        status: str,
        feedback: str,
        thought_process: str
    ):
        """Save agent state."""
        async with self.SessionLocal() as session:
            state = AgentState(
                session_id=session_id,
                message=message,
                status=status,
                feedback=feedback,
                thought_process=thought_process
            )
            session.add(state)
            await session.commit()
    
    async def get_agent_state(self, session_id: str) -> Optional[Dict]:
        """Get latest agent state for a session."""
        async with self.SessionLocal() as session:
            result = await session.execute(
                text("SELECT * FROM agent_states WHERE session_id = :session_id ORDER BY timestamp DESC LIMIT 1"),
                {"session_id": session_id}
            )
            state = result.fetchone()
            if state:
                return {
                    "message": state.message,
                    "status": state.status,
                    "feedback": state.feedback,
                    "thought_process": state.thought_process,
                    "timestamp": state.timestamp.isoformat()
                }
            return None
    
    # API Key management
    async def store_api_key(self, service_name: str, api_key: str):
        """Store encrypted API key."""
        encrypted_key = self.cipher.encrypt(api_key.encode())
        
        async with self.SessionLocal() as session:
            # Check if key exists
            result = await session.execute(
                text("SELECT * FROM api_keys WHERE service_name = :service_name"),
                {"service_name": service_name}
            )
            existing = result.fetchone()
            
            if existing:
                # Update existing key
                await session.execute(
                    text("UPDATE api_keys SET encrypted_key = :key, updated_at = :now WHERE service_name = :service_name"),
                    {
                        "key": encrypted_key,
                        "service_name": service_name,
                        "now": datetime.utcnow()
                    }
                )
            else:
                # Create new key
                api_key_obj = APIKey(
                    service_name=service_name,
                    encrypted_key=encrypted_key
                )
                session.add(api_key_obj)
            
            await session.commit()
    
    async def get_api_key(self, service_name: str) -> Optional[str]:
        """Get decrypted API key."""
        async with self.SessionLocal() as session:
            result = await session.execute(
                text("SELECT encrypted_key FROM api_keys WHERE service_name = :service_name AND is_active = true"),
                {"service_name": service_name}
            )
            api_key = result.fetchone()
            if api_key:
                try:
                    decrypted = self.cipher.decrypt(api_key.encrypted_key)
                    return decrypted.decode()
                except Exception as e:
                    logger.error(f"Error decrypting API key: {e}")
                    return None
            return None
    
    async def list_api_keys(self) -> List[str]:
        """List available API key services."""
        async with self.SessionLocal() as session:
            result = await session.execute(
                text("SELECT service_name FROM api_keys WHERE is_active = true")
            )
            return [row.service_name for row in result.fetchall()]
    
    # Performance metrics
    async def record_metric(self, metric_name: str, metric_value: str, session_id: Optional[str] = None):
        """Record a performance metric."""
        async with self.SessionLocal() as session:
            metric = PerformanceMetric(
                metric_name=metric_name,
                metric_value=metric_value,
                session_id=session_id
            )
            session.add(metric)
            await session.commit()

# Global database manager instance
db_manager = DatabaseManager() 