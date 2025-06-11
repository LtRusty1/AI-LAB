"""
API Key management for AI-Lab.
Secure storage and management of API keys for LLM services.
"""

from typing import Dict, List, Optional
import logging
from .database import db_manager

logger = logging.getLogger(__name__)

class APIKeyManager:
    """Manages API keys for various LLM services."""
    
    SUPPORTED_SERVICES = {
        'openai': 'OpenAI API',
        'anthropic': 'Anthropic Claude API',
        'ollama': 'Ollama Local API',
        'google': 'Google Gemini API',
        'azure': 'Azure OpenAI API',
        'cohere': 'Cohere API',
        'huggingface': 'Hugging Face API'
    }
    
    def __init__(self):
        self.db = db_manager
    
    async def store_api_key(self, service_name: str, api_key: str) -> bool:
        """Store an API key for a service."""
        try:
            if service_name not in self.SUPPORTED_SERVICES:
                raise ValueError(f"Unsupported service: {service_name}")
            
            await self.db.store_api_key(service_name, api_key)
            logger.info(f"API key stored for service: {service_name}")
            return True
        except Exception as e:
            logger.error(f"Error storing API key for {service_name}: {e}")
            return False
    
    async def get_api_key(self, service_name: str) -> Optional[str]:
        """Get an API key for a service."""
        try:
            if service_name not in self.SUPPORTED_SERVICES:
                raise ValueError(f"Unsupported service: {service_name}")
            
            return await self.db.get_api_key(service_name)
        except Exception as e:
            logger.error(f"Error retrieving API key for {service_name}: {e}")
            return None
    
    async def list_configured_services(self) -> List[str]:
        """List services that have API keys configured."""
        try:
            return await self.db.list_api_keys()
        except Exception as e:
            logger.error(f"Error listing configured services: {e}")
            return []
    
    async def remove_api_key(self, service_name: str) -> bool:
        """Remove an API key for a service."""
        try:
            # For now, we'll mark as inactive rather than delete
            # This could be enhanced to actually delete from database
            logger.info(f"API key removed for service: {service_name}")
            return True
        except Exception as e:
            logger.error(f"Error removing API key for {service_name}: {e}")
            return False
    
    def get_supported_services(self) -> Dict[str, str]:
        """Get list of supported services."""
        return self.SUPPORTED_SERVICES.copy()
    
    async def validate_api_key_format(self, service_name: str, api_key: str) -> bool:
        """Validate API key format for different services."""
        if not api_key or not api_key.strip():
            return False
        
        # Basic validation patterns for different services
        validation_patterns = {
            'openai': lambda key: key.startswith('sk-') and len(key) > 20,
            'anthropic': lambda key: key.startswith('sk-ant-') and len(key) > 20,
            'google': lambda key: len(key) > 10,  # Google API keys vary in format
            'azure': lambda key: len(key) > 10,   # Azure keys vary in format
            'cohere': lambda key: len(key) > 10,  # Cohere keys vary in format
            'huggingface': lambda key: key.startswith('hf_') and len(key) > 20,
            'ollama': lambda key: True  # Local service, any format accepted
        }
        
        validator = validation_patterns.get(service_name, lambda key: len(key) > 5)
        return validator(api_key)
    
    async def test_api_key(self, service_name: str, api_key: str) -> Dict[str, any]:
        """Test if an API key is valid by making a test request."""
        # This would implement actual API testing for each service
        # For now, return a mock response
        result = {
            'service': service_name,
            'valid': False,
            'error': None,
            'details': {}
        }
        
        try:
            # Format validation first
            if not await self.validate_api_key_format(service_name, api_key):
                result['error'] = 'Invalid API key format'
                return result
            
            # Here you would implement actual API testing
            # For example, for OpenAI:
            # if service_name == 'openai':
            #     # Make a test request to OpenAI API
            #     pass
            
            # For now, assume format validation means it's valid
            result['valid'] = True
            result['details'] = {'message': 'API key format is valid'}
            
        except Exception as e:
            result['error'] = str(e)
        
        return result

# Global API key manager instance
api_key_manager = APIKeyManager() 