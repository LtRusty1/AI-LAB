"""
Script to run the FastAPI server with uvicorn.
"""

import uvicorn
import logging
from ai_lab.config.config_manager import ConfigManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Run the FastAPI server."""
    try:
        # Load configuration
        config = ConfigManager().get_config()
        
        # Configure uvicorn
        uvicorn_config = {
            "app": "ai_lab.api.app:app",
            "host": config.server.host,
            "port": config.server.port,
            "reload": config.server.reload,
            "workers": config.server.workers,
            "log_level": "info",
            "access_log": True,
            "proxy_headers": True,
            "forwarded_allow_ips": "*"
        }
        
        logger.info(f"Starting server on {config.server.host}:{config.server.port}")
        uvicorn.run(**uvicorn_config)
        
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise

if __name__ == "__main__":
    main() 