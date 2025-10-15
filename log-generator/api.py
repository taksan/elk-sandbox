"""
FastAPI application for log generator management
"""
import time
import random
import threading
from typing import Optional
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from log_generator import LogGeneratorConfig, run_log_generator, get_region_ip_ranges

# Initialize FastAPI app
app = FastAPI(title="Log Generator API", version="1.0.0")

# Global configuration instance
config = LogGeneratorConfig()


# API Models
class IntervalUpdate(BaseModel):
    """Model for updating log generation interval."""
    min_interval: float
    max_interval: float


class DDoSSimulation(BaseModel):
    """Model for DDoS simulation parameters."""
    duration_seconds: int
    region: Optional[str] = None


# API Endpoints
@app.get("/")
async def root():
    """API status and information."""
    return {
        "service": "Log Generator API",
        "status": "running",
        "config": {
            "min_interval": config.min_interval,
            "max_interval": config.max_interval,
            "ddos_active": config.ddos_active,
            "ddos_region": config.ddos_region if config.ddos_active else None
        }
    }


@app.post("/update_interval")
async def update_interval(interval: IntervalUpdate):
    """Update log generation interval."""
    if interval.min_interval < 0 or interval.max_interval < 0:
        return {"error": "Intervals must be positive"}
    if interval.min_interval > interval.max_interval:
        return {"error": "min_interval must be less than or equal to max_interval"}
    
    config.min_interval = interval.min_interval
    config.max_interval = interval.max_interval
    
    return {
        "status": "success",
        "message": "Interval updated",
        "min_interval": config.min_interval,
        "max_interval": config.max_interval
    }


@app.post("/simulate_ddos")
async def simulate_ddos(ddos: DDoSSimulation):
    """Simulate DDoS attack from a specific region."""
    if ddos.duration_seconds <= 0:
        return {"error": "Duration must be positive"}
    
    # Select random region if not specified
    regions = list(get_region_ip_ranges().keys())
    selected_region = ddos.region if ddos.region in regions else random.choice(regions)
    
    config.ddos_active = True
    config.ddos_region = selected_region
    config.ddos_end_time = time.time() + ddos.duration_seconds
    
    return {
        "status": "success",
        "message": f"DDoS simulation started from {selected_region}",
        "region": selected_region,
        "duration_seconds": ddos.duration_seconds,
        "end_time": datetime.fromtimestamp(config.ddos_end_time).isoformat()
    }


@app.get("/status")
async def get_status():
    """Get current generator status."""
    return {
        "min_interval": config.min_interval,
        "max_interval": config.max_interval,
        "ddos_active": config.ddos_active,
        "ddos_region": config.ddos_region if config.ddos_active else None,
        "ddos_remaining": max(0, config.ddos_end_time - time.time()) if config.ddos_active else 0
    }


if __name__ == "__main__":
    # Start log generator in background thread
    generator_thread = threading.Thread(target=run_log_generator, args=(config,), daemon=True)
    generator_thread.start()
    
    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)
