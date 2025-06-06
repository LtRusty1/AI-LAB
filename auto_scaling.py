import os
import psutil
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemMonitor:
    def __init__(self):
        self.metrics = {
            "cpu_usage": 0,
            "memory_usage": 0,
            "response_times": [],
            "error_rates": []
        }
    
    def update_metrics(self):
        self.metrics["cpu_usage"] = psutil.cpu_percent()
        self.metrics["memory_usage"] = psutil.virtual_memory().percent
        return self.metrics

class ConfigManager:
    def __init__(self, config_file: str = "agent_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {
            "max_agents": 5,
            "auto_scale_threshold": 80,
            "response_time_threshold": 5.0,
            "error_rate_threshold": 0.1
        }
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

class AutoScaler:
    def __init__(self):
        self.monitor = SystemMonitor()
        self.config = ConfigManager()
        self.observer = Observer()
        self.setup_file_watcher()
    
    def setup_file_watcher(self):
        class ConfigHandler(FileSystemEventHandler):
            def on_modified(self, event):
                if event.src_path.endswith('agent_config.json'):
                    logger.info("Configuration file changed, reloading...")
                    self.config.load_config()
        
        self.observer.schedule(ConfigHandler(), path='.', recursive=False)
        self.observer.start()
    
    def should_scale(self) -> bool:
        metrics = self.monitor.update_metrics()
        
        # Check CPU and memory usage
        if (metrics["cpu_usage"] > self.config.config["auto_scale_threshold"] or
            metrics["memory_usage"] > self.config.config["auto_scale_threshold"]):
            return True
        
        # Check response times
        if metrics["response_times"]:
            avg_response_time = sum(metrics["response_times"]) / len(metrics["response_times"])
            if avg_response_time > self.config.config["response_time_threshold"]:
                return True
        
        # Check error rates
        if metrics["error_rates"]:
            avg_error_rate = sum(metrics["error_rates"]) / len(metrics["error_rates"])
            if avg_error_rate > self.config.config["error_rate_threshold"]:
                return True
        
        return False
    
    def scale_resources(self):
        if self.should_scale():
            logger.info("Scaling resources...")
            # Implement scaling logic here
            # This could involve:
            # 1. Creating new agent instances
            # 2. Adjusting resource allocations
            # 3. Modifying the agent graph
            pass
    
    def cleanup(self):
        self.observer.stop()
        self.observer.join() 