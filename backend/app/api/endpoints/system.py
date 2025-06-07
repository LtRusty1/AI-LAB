from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import psutil
import GPUtil
from datetime import datetime

router = APIRouter()

class GPUStats(BaseModel):
    memory_used: int
    memory_total: int
    utilization: int
    temperature: float

class SystemStats(BaseModel):
    gpu: Optional[GPUStats]
    timestamp: str

@router.get("/stats", response_model=SystemStats)
async def get_system_stats():
    try:
        # Get GPU stats if available
        gpu_stats = None
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # Get first GPU
                gpu_stats = GPUStats(
                    memory_used=int(gpu.memoryUsed),
                    memory_total=int(gpu.memoryTotal),
                    utilization=int(gpu.load * 100),
                    temperature=float(gpu.temperature)
                )
        except Exception as e:
            # Log error but don't fail the request
            print(f"Error getting GPU stats: {e}")

        return SystemStats(
            gpu=gpu_stats,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 