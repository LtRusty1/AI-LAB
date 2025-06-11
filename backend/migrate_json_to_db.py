#!/usr/bin/env python3
"""
Migration utility to transfer JSON conversation data to PostgreSQL database.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import logging

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from ai_lab.database import db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def migrate_conversations():
    """Migrate conversation files from JSON to database."""
    conversations_dir = Path("conversations")
    
    if not conversations_dir.exists():
        logger.info("No conversations directory found")
        return 0
    
    json_files = list(conversations_dir.glob("*.json"))
    if not json_files:
        logger.info("No JSON conversation files found")
        return 0
    
    logger.info(f"Found {len(json_files)} conversation files to migrate")
    migrated_count = 0
    
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                conversation_data = json.load(f)
            
            # Extract session ID from filename
            session_id = json_file.stem
            
            # Handle different JSON formats
            if isinstance(conversation_data, list):
                # Format: list of messages
                for message in conversation_data:
                    await migrate_single_message(session_id, message)
            elif isinstance(conversation_data, dict):
                # Format: single message or conversation object
                if 'messages' in conversation_data:
                    # Contains a messages array
                    for message in conversation_data['messages']:
                        await migrate_single_message(session_id, message)
                else:
                    # Single message object
                    await migrate_single_message(session_id, conversation_data)
            
            migrated_count += 1
            logger.info(f"✅ Migrated {json_file.name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to migrate {json_file.name}: {e}")
    
    return migrated_count

async def migrate_single_message(session_id: str, message_data: dict):
    """Migrate a single message to the database."""
    try:
        # Extract message fields with defaults
        role = message_data.get('role', 'unknown')
        content = message_data.get('content', message_data.get('message', ''))
        thought_process = message_data.get('thought_process')
        
        # Handle timestamp
        timestamp_str = message_data.get('timestamp')
        if timestamp_str:
            try:
                # Try to parse ISO format
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except:
                # Fallback to current time
                timestamp = datetime.utcnow()
        else:
            timestamp = datetime.utcnow()
        
        # Add to database
        await db_manager.add_conversation_message(
            session_id=session_id,
            role=role,
            content=content,
            thought_process=thought_process
        )
        
    except Exception as e:
        logger.error(f"Error migrating message: {e}")
        raise

async def migrate_agent_states():
    """Migrate agent state files from JSON to database."""
    states_dir = Path("states")
    
    if not states_dir.exists():
        logger.info("No states directory found")
        return 0
    
    json_files = list(states_dir.glob("*.json"))
    if not json_files:
        logger.info("No JSON state files found")
        return 0
    
    logger.info(f"Found {len(json_files)} state files to migrate")
    migrated_count = 0
    
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                state_data = json.load(f)
            
            # Extract session ID from filename
            session_id = json_file.stem
            
            # Migrate state data
            await db_manager.save_agent_state(
                session_id=session_id,
                message=state_data.get('message', ''),
                status=state_data.get('status', 'unknown'),
                feedback=state_data.get('feedback', ''),
                thought_process=state_data.get('thought_process', '')
            )
            
            migrated_count += 1
            logger.info(f"✅ Migrated state {json_file.name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to migrate state {json_file.name}: {e}")
    
    return migrated_count

async def backup_json_files():
    """Create a backup of JSON files before migration."""
    backup_dir = Path("json_backup")
    backup_dir.mkdir(exist_ok=True)
    
    # Backup conversations
    conversations_dir = Path("conversations")
    if conversations_dir.exists():
        for json_file in conversations_dir.glob("*.json"):
            backup_file = backup_dir / f"conversations_{json_file.name}"
            with open(json_file, 'r') as src, open(backup_file, 'w') as dst:
                dst.write(src.read())
    
    # Backup states
    states_dir = Path("states")
    if states_dir.exists():
        for json_file in states_dir.glob("*.json"):
            backup_file = backup_dir / f"states_{json_file.name}"
            with open(json_file, 'r') as src, open(backup_file, 'w') as dst:
                dst.write(src.read())
    
    logger.info(f"✅ JSON files backed up to {backup_dir}")

async def main():
    """Main migration function."""
    print("🔄 AI-Lab JSON to Database Migration")
    print("=" * 50)
    
    # Check database connection
    try:
        await db_manager.create_tables()
        logger.info("✅ Database connection successful")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return
    
    # Create backup
    print("\n📁 Creating backup of JSON files...")
    await backup_json_files()
    
    # Migrate conversations
    print("\n💬 Migrating conversations...")
    conversations_migrated = await migrate_conversations()
    
    # Migrate agent states
    print("\n🤖 Migrating agent states...")
    states_migrated = await migrate_agent_states()
    
    print(f"\n✅ Migration completed!")
    print(f"   - Conversations migrated: {conversations_migrated}")
    print(f"   - Agent states migrated: {states_migrated}")
    print(f"   - Backup created in: json_backup/")
    
    if conversations_migrated > 0 or states_migrated > 0:
        print("\n⚠️  You can now safely archive or delete the original JSON files")
        print("   The data has been successfully transferred to the database.")

if __name__ == "__main__":
    asyncio.run(main()) 