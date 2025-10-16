"""
FastAPI application for traffic generator management
"""
import time
import random
import threading
from typing import Optional
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from traffic_generator import LogGeneratorConfig, run_log_generator, get_region_ip_ranges

# Initialize FastAPI app
app = FastAPI(title="Traffic Generator API", version="1.0.0")

# Global configuration instance
config = LogGeneratorConfig()


# API Models
class IntervalUpdate(BaseModel):
    """Model for updating traffic generation interval."""
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
        "service": "Traffic Generator API",
        "status": "running" if config.traffic_enabled else "paused",
        "config": {
            "traffic_enabled": config.traffic_enabled,
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
        "traffic_enabled": config.traffic_enabled,
        "min_interval": config.min_interval,
        "max_interval": config.max_interval,
        "ddos_active": config.ddos_active,
        "ddos_region": config.ddos_region if config.ddos_active else None,
        "ddos_remaining": max(0, config.ddos_end_time - time.time()) if config.ddos_active else 0,
        "active_flows": config.flow_manager.get_active_flow_count()
    }


@app.post("/traffic/start")
async def start_traffic():
    """Start traffic generation."""
    if config.traffic_enabled:
        return {
            "status": "info",
            "message": "Traffic generation is already running"
        }
    
    config.traffic_enabled = True
    return {
        "status": "success",
        "message": "Traffic generation started",
        "traffic_enabled": config.traffic_enabled
    }


@app.post("/traffic/stop")
async def stop_traffic():
    """Stop traffic generation."""
    if not config.traffic_enabled:
        return {
            "status": "info",
            "message": "Traffic generation is already stopped"
        }
    
    config.traffic_enabled = False
    return {
        "status": "success",
        "message": "Traffic generation stopped",
        "traffic_enabled": config.traffic_enabled
    }


@app.post("/traffic/pause")
async def pause_traffic():
    """Pause traffic generation (alias for stop)."""
    return await stop_traffic()


@app.post("/traffic/resume")
async def resume_traffic():
    """Resume traffic generation (alias for start)."""
    return await start_traffic()


if __name__ == "__main__":
    # Start log generator in background thread
    generator_thread = threading.Thread(target=run_log_generator, args=(config,), daemon=True)
    generator_thread.start()
    
    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)
