"""
Performance monitoring and profiling for AI-Lab.
Tracks LLM inference times, I/O operations, and system metrics.
"""

import time
import psutil
import GPUtil
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from functools import wraps
import logging
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from .database import db_manager

logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('ai_lab_requests_total', 'Total requests', ['endpoint'])
REQUEST_DURATION = Histogram('ai_lab_request_duration_seconds', 'Request duration', ['endpoint'])
LLM_INFERENCE_TIME = Histogram('ai_lab_llm_inference_seconds', 'LLM inference time')
GPU_UTILIZATION = Gauge('ai_lab_gpu_utilization_percent', 'GPU utilization percentage')
MEMORY_USAGE = Gauge('ai_lab_memory_usage_bytes', 'Memory usage in bytes')
CPU_USAGE = Gauge('ai_lab_cpu_usage_percent', 'CPU usage percentage')

class PerformanceMonitor:
    """Performance monitoring and benchmarking."""
    
    def __init__(self):
        self.db = db_manager
        self.start_time = time.time()
        
    async def record_metric(self, metric_name: str, metric_value: Any, session_id: Optional[str] = None):
        """Record a performance metric."""
        try:
            await self.db.record_metric(metric_name, str(metric_value), session_id)
        except Exception as e:
            logger.error(f"Error recording metric: {e}")
    
    def time_operation(self, operation_name: str):
        """Decorator to time operations."""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    # Record to Prometheus
                    REQUEST_DURATION.labels(endpoint=operation_name).observe(duration)
                    REQUEST_COUNT.labels(endpoint=operation_name).inc()
                    
                    # Record to database
                    await self.record_metric(f"{operation_name}_duration", duration)
                    
                    logger.info(f"{operation_name} completed in {duration:.2f}s")
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    await self.record_metric(f"{operation_name}_error", str(e))
                    logger.error(f"{operation_name} failed after {duration:.2f}s: {e}")
                    raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    # Record to Prometheus
                    REQUEST_DURATION.labels(endpoint=operation_name).observe(duration)
                    REQUEST_COUNT.labels(endpoint=operation_name).inc()
                    
                    logger.info(f"{operation_name} completed in {duration:.2f}s")
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    logger.error(f"{operation_name} failed after {duration:.2f}s: {e}")
                    raise
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    async def collect_system_metrics(self):
        """Collect current system metrics."""
        metrics = {}
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        metrics['cpu_usage_percent'] = cpu_percent
        CPU_USAGE.set(cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        metrics['memory_usage_bytes'] = memory.used
        metrics['memory_usage_percent'] = memory.percent
        MEMORY_USAGE.set(memory.used)
        
        # GPU metrics (if available)
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # Primary GPU
                metrics['gpu_utilization_percent'] = gpu.load * 100
                metrics['gpu_memory_used_mb'] = gpu.memoryUsed
                metrics['gpu_memory_total_mb'] = gpu.memoryTotal
                metrics['gpu_temperature_c'] = gpu.temperature
                
                GPU_UTILIZATION.set(gpu.load * 100)
        except Exception as e:
            logger.debug(f"GPU metrics not available: {e}")
        
        # Record all metrics
        for metric_name, value in metrics.items():
            await self.record_metric(metric_name, value)
        
        return metrics
    
    async def benchmark_llm_inference(self, model_name: str, prompt: str, iterations: int = 5) -> Dict:
        """Benchmark LLM inference performance."""
        results = {
            'model_name': model_name,
            'prompt_length': len(prompt),
            'iterations': iterations,
            'times': [],
            'avg_time': 0,
            'min_time': float('inf'),
            'max_time': 0,
            'total_time': 0
        }
        
        for i in range(iterations):
            start_time = time.time()
            
            # This would call your actual LLM inference
            # For now, we'll simulate it
            await asyncio.sleep(0.1)  # Simulate inference time
            
            duration = time.time() - start_time
            results['times'].append(duration)
            results['total_time'] += duration
            results['min_time'] = min(results['min_time'], duration)
            results['max_time'] = max(results['max_time'], duration)
            
            # Record individual inference time
            LLM_INFERENCE_TIME.observe(duration)
            await self.record_metric('llm_inference_time', duration)
        
        results['avg_time'] = results['total_time'] / iterations
        
        # Record benchmark results
        await self.record_metric('llm_benchmark_avg_time', results['avg_time'])
        await self.record_metric('llm_benchmark_min_time', results['min_time'])
        await self.record_metric('llm_benchmark_max_time', results['max_time'])
        
        return results
    
    async def get_performance_summary(self, hours: int = 24) -> Dict:
        """Get performance summary for the last N hours."""
        # This would query the database for metrics
        # For now, return current system state
        system_metrics = await self.collect_system_metrics()
        
        summary = {
            'uptime_seconds': time.time() - self.start_time,
            'current_metrics': system_metrics,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return summary
    
    def get_prometheus_metrics(self) -> str:
        """Get Prometheus-formatted metrics."""
        return generate_latest().decode('utf-8')

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

# Decorator for easy use
def monitor_performance(operation_name: str):
    """Decorator to monitor performance of functions."""
    return performance_monitor.time_operation(operation_name) 