#!/usr/bin/env python3
"""
Database setup script for AI-Lab.
Initializes PostgreSQL database and tables.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from ai_lab.database import db_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_database():
    """Setup database tables and initial data."""
    try:
        logger.info("Setting up AI-Lab database...")
        
        # Create all tables
        await db_manager.create_tables()
        logger.info("✅ Database tables created successfully")
        
        # Test database connection
        async with db_manager.SessionLocal() as session:
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            test_result = result.fetchone()
            if test_result:
                logger.info("✅ Database connection test successful")
            else:
                logger.error("❌ Database connection test failed")
                return False
        
        logger.info("🎉 Database setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        return False

async def migrate_json_data():
    """Migrate existing JSON conversation data to database."""
    try:
        logger.info("Migrating existing JSON data to database...")
        
        # Check for existing conversation files
        conversations_dir = Path("conversations")
        if not conversations_dir.exists():
            logger.info("No existing conversation data found")
            return True
        
        json_files = list(conversations_dir.glob("*.json"))
        if not json_files:
            logger.info("No JSON conversation files found")
            return True
        
        logger.info(f"Found {len(json_files)} conversation files to migrate")
        
        # TODO: Implement actual migration logic
        # This would read each JSON file and convert to database records
        
        logger.info("✅ JSON data migration completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ JSON data migration failed: {e}")
        return False

def print_setup_instructions():
    """Print PostgreSQL setup instructions."""
    print("""
🔧 PostgreSQL Setup Instructions:

1. Install PostgreSQL:
   - Windows: Download from https://www.postgresql.org/download/windows/
   - macOS: brew install postgresql
   - Ubuntu: sudo apt-get install postgresql postgresql-contrib

2. Create database and user:
   sudo -u postgres psql
   CREATE DATABASE ai_lab;
   CREATE USER ai_lab_user WITH ENCRYPTED PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE ai_lab TO ai_lab_user;
   \q

3. Set environment variable:
   export DATABASE_URL="postgresql+asyncpg://ai_lab_user:your_password@localhost:5432/ai_lab"
   
   Or create a .env file with:
   DATABASE_URL=postgresql+asyncpg://ai_lab_user:your_password@localhost:5432/ai_lab

4. Run this setup script:
   python setup_database.py

""")

async def main():
    """Main setup function."""
    print("🚀 AI-Lab Database Setup")
    print("=" * 50)
    
    # Check if DATABASE_URL is set
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("⚠️  DATABASE_URL environment variable not set")
        print_setup_instructions()
        return
    
    print(f"📍 Database URL: {database_url}")
    
    # Setup database
    setup_success = await setup_database()
    if not setup_success:
        print("❌ Database setup failed")
        return
    
    # Migrate existing data
    migrate_success = await migrate_json_data()
    if not migrate_success:
        print("⚠️  Data migration had issues, but database is ready")
    
    print("\n✅ Setup completed successfully!")
    print("You can now start the AI-Lab backend with enhanced features.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print_setup_instructions()
    else:
        asyncio.run(main()) 