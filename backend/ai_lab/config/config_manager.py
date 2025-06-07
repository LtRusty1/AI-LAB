"""
Configuration manager for handling system settings and environment variables.
Provides a centralized way to manage configuration with proper validation and type safety.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
import toml
from pydantic import BaseModel, Field, validator
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class DatabaseConfig(BaseModel):
    """Database configuration settings."""
    url: str = "sqlite:///ai_lab.db"
    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False
    pool_timeout: int = 30
    pool_recycle: int = 3600

class RedisConfig(BaseModel):
    """Redis configuration settings."""
    url: str = "redis://localhost:6379"
    password: Optional[str] = None
    db: int = 0
    max_connections: int = 10
    socket_timeout: int = 5
    socket_connect_timeout: int = 5

class GPUConfig(BaseModel):
    """GPU configuration settings."""
    enabled: bool = True
    device_id: int = 0
    memory_limit: Optional[int] = None
    precision: str = "fp16"
    batch_size: int = 32
    num_workers: Optional[int] = None

class OllamaConfig(BaseModel):
    """Ollama configuration settings."""
    base_url: str = "http://localhost:11434/v1"
    model_name: str = "mistral"
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

class LoggingConfig(BaseModel):
    """Logging configuration settings."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None
    max_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

class SecurityConfig(BaseModel):
    """Security configuration settings."""
    tls_enabled: bool = False
    cert_file: Optional[str] = None
    key_file: Optional[str] = None
    allowed_origins: list[str] = ["*"]
    jwt_secret: Optional[str] = None
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

class SystemConfig(BaseModel):
    """Main system configuration."""
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    gpu: GPUConfig = Field(default_factory=GPUConfig)
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    
    @validator("security")
    def validate_security(cls, v: SecurityConfig) -> SecurityConfig:
        """Validate security configuration."""
        if v.tls_enabled:
            if not v.cert_file or not v.key_file:
                raise ValueError("TLS enabled but certificate files not specified")
            if not os.path.exists(v.cert_file):
                raise ValueError(f"Certificate file not found: {v.cert_file}")
            if not os.path.exists(v.key_file):
                raise ValueError(f"Key file not found: {v.key_file}")
        return v

class ConfigManager:
    """Manages system configuration with environment variable support."""
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config: Optional[SystemConfig] = None
        self._load_environment()
    
    def _load_environment(self) -> None:
        """Load environment variables from .env file."""
        env_file = self.config_dir / ".env"
        if env_file.exists():
            load_dotenv(env_file)
    
    def _get_env_value(self, key: str, default: Any = None) -> Any:
        """
        Get value from environment variable with type conversion.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            
        Returns:
            Any: Environment variable value
        """
        value = os.getenv(key)
        if value is None:
            return default
        
        # Try to convert to appropriate type
        if isinstance(default, bool):
            return value.lower() in ("true", "1", "yes")
        elif isinstance(default, int):
            return int(value)
        elif isinstance(default, float):
            return float(value)
        return value
    
    def load_config(self) -> SystemConfig:
        """
        Load configuration from files and environment variables.
        
        Returns:
            SystemConfig: Loaded configuration
        """
        try:
            # Try to load from YAML first
            yaml_config = self.config_dir / "config.yaml"
            if yaml_config.exists():
                with open(yaml_config) as f:
                    config_data = yaml.safe_load(f)
            else:
                # Try TOML as fallback
                toml_config = self.config_dir / "config.toml"
                if toml_config.exists():
                    with open(toml_config) as f:
                        config_data = toml.load(f)
                else:
                    config_data = {}
            
            # Override with environment variables
            env_prefix = "AI_LAB_"
            for key, value in os.environ.items():
                if key.startswith(env_prefix):
                    config_key = key[len(env_prefix):].lower()
                    # Convert key to nested dict path
                    parts = config_key.split("_")
                    current = config_data
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    current[parts[-1]] = value
            
            # Create config object
            self.config = SystemConfig(**config_data)
            return self.config
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            raise RuntimeError(f"Configuration loading failed: {str(e)}")
    
    def save_config(self, config: Optional[SystemConfig] = None) -> None:
        """
        Save configuration to file.
        
        Args:
            config: Configuration to save (uses current if None)
        """
        if config is None:
            config = self.config
        if config is None:
            raise RuntimeError("No configuration to save")
        
        try:
            # Convert to dict
            config_data = config.model_dump()
            
            # Save as YAML
            yaml_config = self.config_dir / "config.yaml"
            with open(yaml_config, "w") as f:
                yaml.dump(config_data, f, default_flow_style=False)
            
            logger.info(f"Configuration saved to {yaml_config}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
            raise RuntimeError(f"Configuration saving failed: {str(e)}")
    
    def get_config(self) -> SystemConfig:
        """
        Get current configuration.
        
        Returns:
            SystemConfig: Current configuration
        """
        if self.config is None:
            self.config = self.load_config()
        return self.config
    
    def update_config(self, **kwargs) -> SystemConfig:
        """
        Update configuration with new values.
        
        Args:
            **kwargs: Configuration values to update
            
        Returns:
            SystemConfig: Updated configuration
        """
        if self.config is None:
            self.config = self.load_config()
        
        # Update config
        config_data = self.config.model_dump()
        config_data.update(kwargs)
        self.config = SystemConfig(**config_data)
        
        # Save changes
        self.save_config()
        return self.config 