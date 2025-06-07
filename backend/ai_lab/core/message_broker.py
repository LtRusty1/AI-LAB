"""
Redis-based message broker for agent communication.
Implements a robust pub/sub system with message persistence and error handling.
"""

import asyncio
import json
from typing import AsyncGenerator, Dict, List, Optional, Set
import aioredis
from datetime import datetime, timedelta

from ..models.base import AgentMessage, MessageType, SystemConfig

class MessageBroker:
    """Redis-based message broker for agent communication."""
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.redis: Optional[aioredis.Redis] = None
        self._subscribers: Dict[str, Set[asyncio.Queue]] = {}
        self._message_ttl = timedelta(days=7)  # Messages expire after 7 days
        
    async def connect(self) -> None:
        """Connect to Redis and initialize the broker."""
        try:
            self.redis = await aioredis.from_url(
                self.config.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await self.redis.ping()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Redis: {str(e)}")
    
    async def disconnect(self) -> None:
        """Disconnect from Redis and cleanup resources."""
        if self.redis:
            await self.redis.close()
            self.redis = None
    
    async def publish(self, message: AgentMessage) -> None:
        """
        Publish a message to the specified channel.
        
        Args:
            message: The message to publish
        """
        if not self.redis:
            raise RuntimeError("Message broker not connected")
        
        try:
            # Convert message to JSON
            message_data = message.model_dump_json()
            
            # Publish to specific channel if receiver_id is set
            if message.receiver_id:
                channel = f"agent:{message.receiver_id}"
                await self.redis.publish(channel, message_data)
            
            # Always publish to broadcast channel
            await self.redis.publish("broadcast", message_data)
            
            # Store message in Redis for persistence
            message_key = f"message:{message.id}"
            await self.redis.setex(
                message_key,
                self._message_ttl,
                message_data
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to publish message: {str(e)}")
    
    async def subscribe(self, agent_id: str) -> AsyncGenerator[AgentMessage, None]:
        """
        Subscribe to messages for a specific agent.
        
        Args:
            agent_id: The ID of the agent to subscribe for
            
        Yields:
            AgentMessage: Messages received by the agent
        """
        if not self.redis:
            raise RuntimeError("Message broker not connected")
        
        # Create subscription queue
        queue = asyncio.Queue()
        channel = f"agent:{agent_id}"
        
        # Add to subscribers
        if channel not in self._subscribers:
            self._subscribers[channel] = set()
        self._subscribers[channel].add(queue)
        
        try:
            # Subscribe to agent-specific channel
            pubsub = self.redis.pubsub()
            await pubsub.subscribe(channel, "broadcast")
            
            # Start message processing loop
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    try:
                        # Parse message data
                        data = json.loads(message["data"])
                        agent_message = AgentMessage.model_validate(data)
                        
                        # Only yield messages intended for this agent
                        if (agent_message.receiver_id is None or 
                            str(agent_message.receiver_id) == agent_id):
                            yield agent_message
                            
                    except Exception as e:
                        print(f"Error processing message: {str(e)}")
                        continue
                
                # Small delay to prevent CPU spinning
                await asyncio.sleep(0.01)
                
        finally:
            # Cleanup
            self._subscribers[channel].remove(queue)
            if not self._subscribers[channel]:
                del self._subscribers[channel]
            await pubsub.unsubscribe()
            await pubsub.close()
    
    async def get_message_history(
        self,
        agent_id: str,
        limit: int = 100,
        message_types: Optional[List[MessageType]] = None
    ) -> List[AgentMessage]:
        """
        Retrieve message history for an agent.
        
        Args:
            agent_id: The ID of the agent
            limit: Maximum number of messages to retrieve
            message_types: Optional filter for message types
            
        Returns:
            List[AgentMessage]: List of historical messages
        """
        if not self.redis:
            raise RuntimeError("Message broker not connected")
        
        try:
            # Get all message keys
            message_keys = await self.redis.keys("message:*")
            messages = []
            
            for key in message_keys[:limit]:
                data = await self.redis.get(key)
                if data:
                    message = AgentMessage.model_validate_json(data)
                    
                    # Apply filters
                    if (message.receiver_id and str(message.receiver_id) == agent_id or
                        message.sender_id and str(message.sender_id) == agent_id):
                        if not message_types or message.type in message_types:
                            messages.append(message)
            
            # Sort by timestamp
            messages.sort(key=lambda x: x.timestamp)
            return messages
            
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve message history: {str(e)}")
    
    async def clear_history(self, before_date: Optional[datetime] = None) -> None:
        """
        Clear message history.
        
        Args:
            before_date: Optional date to clear messages before
        """
        if not self.redis:
            raise RuntimeError("Message broker not connected")
        
        try:
            if before_date:
                # Get all message keys
                message_keys = await self.redis.keys("message:*")
                for key in message_keys:
                    data = await self.redis.get(key)
                    if data:
                        message = AgentMessage.model_validate_json(data)
                        if message.timestamp < before_date:
                            await self.redis.delete(key)
            else:
                # Clear all messages
                message_keys = await self.redis.keys("message:*")
                if message_keys:
                    await self.redis.delete(*message_keys)
                    
        except Exception as e:
            raise RuntimeError(f"Failed to clear message history: {str(e)}") 