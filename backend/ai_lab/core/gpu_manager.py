"""
GPU acceleration manager for handling CUDA operations and resource management.
Provides a unified interface for GPU-accelerated computations and memory management.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
import torch
import cupy as cp
import numpy as np
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class GPUStats:
    """Statistics about GPU usage and performance."""
    total_memory: int
    used_memory: int
    free_memory: int
    utilization: float
    temperature: float
    power_usage: float
    timestamp: datetime = datetime.utcnow()

class GPUManager:
    """Manages GPU resources and provides acceleration utilities."""
    
    def __init__(self, device_id: int = 0, memory_limit: Optional[int] = None):
        """
        Initialize the GPU manager.
        
        Args:
            device_id: CUDA device ID to use
            memory_limit: Optional memory limit in bytes
        """
        self.device_id = device_id
        self.memory_limit = memory_limit
        self._lock = asyncio.Lock()
        self._memory_pool = None
        self._initialize_gpu()
    
    def _initialize_gpu(self) -> None:
        """Initialize GPU and memory pool."""
        try:
            # Set CUDA device
            torch.cuda.set_device(self.device_id)
            cp.cuda.Device(self.device_id).use()
            
            # Get device properties
            self.device = torch.cuda.get_device_properties(self.device_id)
            self.device_name = self.device.name
            self.total_memory = self.device.total_memory
            
            # Set memory limit if specified
            if self.memory_limit:
                torch.cuda.set_per_process_memory_fraction(
                    self.memory_limit / self.total_memory,
                    self.device_id
                )
            
            # Initialize memory pool
            self._memory_pool = cp.cuda.MemoryPool()
            cp.cuda.set_allocator(self._memory_pool.malloc)
            
            logger.info(f"Initialized GPU: {self.device_name}")
            logger.info(f"Total memory: {self.total_memory / 1024**2:.1f} MB")
            
        except Exception as e:
            logger.error(f"Failed to initialize GPU: {str(e)}")
            raise RuntimeError(f"GPU initialization failed: {str(e)}")
    
    async def get_stats(self) -> GPUStats:
        """
        Get current GPU statistics.
        
        Returns:
            GPUStats: Current GPU statistics
        """
        async with self._lock:
            try:
                # Get memory info
                memory_info = torch.cuda.memory_stats(self.device_id)
                total_memory = self.total_memory
                used_memory = memory_info["allocated_bytes.all.current"]
                free_memory = total_memory - used_memory
                
                # Get utilization (requires nvidia-smi)
                try:
                    import pynvml
                    pynvml.nvmlInit()
                    handle = pynvml.nvmlDeviceGetHandleByIndex(self.device_id)
                    utilization = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
                    temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                    power_usage = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to watts
                except:
                    utilization = 0.0
                    temperature = 0.0
                    power_usage = 0.0
                
                return GPUStats(
                    total_memory=total_memory,
                    used_memory=used_memory,
                    free_memory=free_memory,
                    utilization=utilization,
                    temperature=temperature,
                    power_usage=power_usage
                )
                
            except Exception as e:
                logger.error(f"Failed to get GPU stats: {str(e)}")
                raise RuntimeError(f"Failed to get GPU stats: {str(e)}")
    
    async def clear_memory(self) -> None:
        """Clear GPU memory and reset memory pool."""
        async with self._lock:
            try:
                # Clear PyTorch cache
                torch.cuda.empty_cache()
                
                # Clear CuPy memory pool
                if self._memory_pool:
                    self._memory_pool.free_all_blocks()
                
                logger.info("Cleared GPU memory")
                
            except Exception as e:
                logger.error(f"Failed to clear GPU memory: {str(e)}")
                raise RuntimeError(f"Failed to clear GPU memory: {str(e)}")
    
    async def batch_inference(
        self,
        model: torch.nn.Module,
        inputs: List[torch.Tensor],
        batch_size: int = 32
    ) -> List[torch.Tensor]:
        """
        Perform batched inference on GPU.
        
        Args:
            model: PyTorch model to use
            inputs: List of input tensors
            batch_size: Batch size for inference
            
        Returns:
            List[torch.Tensor]: List of output tensors
        """
        async with self._lock:
            try:
                model.eval()
                results = []
                
                # Process in batches
                for i in range(0, len(inputs), batch_size):
                    batch = inputs[i:i + batch_size]
                    
                    # Stack tensors if needed
                    if isinstance(batch[0], torch.Tensor):
                        batch = torch.stack(batch)
                    
                    # Move to GPU
                    batch = batch.cuda()
                    
                    # Run inference
                    with torch.no_grad():
                        outputs = model(batch)
                    
                    # Move back to CPU and add to results
                    results.extend(outputs.cpu())
                
                return results
                
            except Exception as e:
                logger.error(f"Failed to perform batch inference: {str(e)}")
                raise RuntimeError(f"Batch inference failed: {str(e)}")
    
    async def parallel_map(
        self,
        func: callable,
        data: List[Any],
        num_workers: Optional[int] = None
    ) -> List[Any]:
        """
        Parallel map operation using GPU.
        
        Args:
            func: Function to apply
            data: List of data to process
            num_workers: Number of parallel workers
            
        Returns:
            List[Any]: Processed results
        """
        async with self._lock:
            try:
                if num_workers is None:
                    num_workers = torch.cuda.device_count()
                
                # Create CUDA streams
                streams = [torch.cuda.Stream() for _ in range(num_workers)]
                
                # Process data in parallel
                results = [None] * len(data)
                for i, item in enumerate(data):
                    stream = streams[i % num_workers]
                    with torch.cuda.stream(stream):
                        results[i] = func(item)
                
                # Synchronize streams
                torch.cuda.synchronize()
                
                return results
                
            except Exception as e:
                logger.error(f"Failed to perform parallel map: {str(e)}")
                raise RuntimeError(f"Parallel map failed: {str(e)}")
    
    async def optimize_model(
        self,
        model: torch.nn.Module,
        input_shape: Tuple[int, ...],
        precision: str = "fp16"
    ) -> torch.nn.Module:
        """
        Optimize a model for GPU inference.
        
        Args:
            model: PyTorch model to optimize
            input_shape: Shape of input tensors
            precision: Precision to use (fp16, fp32, int8)
            
        Returns:
            torch.nn.Module: Optimized model
        """
        async with self._lock:
            try:
                # Move model to GPU
                model = model.cuda()
                
                # Set precision
                if precision == "fp16":
                    model = model.half()
                elif precision == "int8":
                    model = torch.quantization.quantize_dynamic(
                        model, {torch.nn.Linear}, dtype=torch.qint8
                    )
                
                # Enable cuDNN benchmarking
                torch.backends.cudnn.benchmark = True
                
                # Create example input
                example_input = torch.randn(input_shape).cuda()
                if precision == "fp16":
                    example_input = example_input.half()
                
                # Trace model
                traced_model = torch.jit.trace(model, example_input)
                
                return traced_model
                
            except Exception as e:
                logger.error(f"Failed to optimize model: {str(e)}")
                raise RuntimeError(f"Model optimization failed: {str(e)}")
    
    def __del__(self):
        """Cleanup GPU resources."""
        try:
            if self._memory_pool:
                self._memory_pool.free_all_blocks()
            torch.cuda.empty_cache()
        except:
            pass 