from fastapi import FastAPI, HTTPException, Header, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import secrets
import string
from typing import Optional
import uvicorn
import os

from .models import (
    DeviceHeaders, SetupHeaders, DisplayResponse, SetupResponse,
    DeviceLog, ScreenRequest, ScreenResponse, ErrorResponse
)
from .database import Database
from .image_utils import ImageGenerator
from .models import Device

app = FastAPI(
    title="TRMNL Custom Server",
    description="Custom FastAPI server for TRMNL e-ink devices",
    version="1.0.0"
)

# Initialize components
db = Database()
image_gen = ImageGenerator()

# Mount static files for serving images
os.makedirs("static/images", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

def generate_api_key() -> str:
    """Generate a secure API key."""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

def generate_friendly_id() -> str:
    """Generate a short friendly device ID."""
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))

def get_base_url(request: Request) -> str:
    """Get the base URL for image serving."""
    return f"{request.url.scheme}://{request.headers.get('host', 'localhost')}"

# Authentication removed - all endpoints now have open access

@app.get("/")
async def root():
    """Root endpoint with server status."""
    return {
        "message": "TRMNL Custom Server",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/display", response_model=DisplayResponse)
async def display_endpoint(
    request: Request,
    id: str = Header(..., description="Device MAC address"),
    access_token: str = Header(None, alias="Access-Token"),
    refresh_rate: Optional[int] = Header(None, alias="Refresh-Rate"),
    battery_voltage: Optional[float] = Header(None, alias="Battery-Voltage"),
    fw_version: Optional[str] = Header(None, alias="FW-Version"),
    rssi: Optional[int] = Header(None, alias="RSSI"),
    width: Optional[int] = Header(800, alias="Width"),
    height: Optional[int] = Header(480, alias="Height")
):
    """Primary device endpoint for screen content delivery (open access)."""
    
    # Update device status
    db.update_device_status(
        id,
        last_seen=datetime.utcnow(),
        firmware_version=fw_version,
        battery_voltage=battery_voltage
    )
    
    # Generate or get current image
    base_url = get_base_url(request)
    
    # Create big HELLO WORLD image using proper image generation
    filename, file_path = image_gen.create_hello_world_image()
    image_url = f"{base_url}/static/images/{filename}.png"
    
    return DisplayResponse(
        status=0,
        image_url=image_url,
        filename=filename,
        refresh_rate=60,  # Refresh every 1 minute for faster updates
        update_firmware=False,
        firmware_url=None,
        reset_firmware=False,
        special_function="sleep",
        image_url_timeout=30
    )

@app.post("/api/setup", response_model=SetupResponse)
async def setup_endpoint(
    request: Request,
    id: str = Header(..., description="Device MAC address"),
    fw_version: Optional[str] = Header(None, alias="FW-Version")
):
    """Device provisioning during first boot."""
    
    # Check if device already exists
    existing_device = db.get_device(id)
    if existing_device:
        # Return existing credentials
        filename, _ = image_gen.create_welcome_image(existing_device.friendly_id)
        base_url = get_base_url(request)
        image_url = f"{base_url}/static/images/{filename}.png"
        
        return SetupResponse(
            status=200,
            api_key=existing_device.api_key,
            friendly_id=existing_device.friendly_id,
            image_url=image_url,
            message="Welcome back to your TRMNL server"
        )
    
    # Create new device
    api_key = generate_api_key()
    friendly_id = generate_friendly_id()
    
    new_device = Device(
        mac_address=id,
        api_key=api_key,
        friendly_id=friendly_id,
        created_at=datetime.utcnow(),
        firmware_version=fw_version
    )
    
    db.create_device(new_device)
    
    # Create welcome image
    filename, _ = image_gen.create_welcome_image(friendly_id)
    base_url = get_base_url(request)
    image_url = f"{base_url}/static/images/{filename}.png"
    
    return SetupResponse(
        status=200,
        api_key=api_key,
        friendly_id=friendly_id,
        image_url=image_url,
        message="Welcome to your custom TRMNL server"
    )

@app.post("/api/log")
async def log_endpoint(
    log_data: DeviceLog,
    id: str = Header(..., description="Device MAC address"),
    access_token: str = Header(None, alias="Access-Token")
):
    """Device telemetry and logging endpoint (open access)."""
    
    # Store device log data (use MAC address from header)
    db.log_device_data(id, log_data)
    
    # Update device status with latest telemetry if device exists
    existing_device = db.get_device(id)
    if existing_device:
        db.update_device_status(
            id,
            last_seen=datetime.utcnow(),
            firmware_version=log_data.firmware_version,
            battery_voltage=log_data.battery_voltage
        )
    
    return {"status": "success", "message": "Log data received"}

@app.post("/api/screens", response_model=ScreenResponse)
async def create_screen(
    screen_request: ScreenRequest,
    request: Request,
    access_token: str = Header(None, alias="Access-Token")
):
    """Create new screen content programmatically (open access)."""
    
    base_url = get_base_url(request)
    
    if screen_request.content_type == "html":
        filename, file_path = image_gen.html_to_image(
            screen_request.content, 
            screen_request.filename
        )
    else:
        # For other content types, treat as text for now
        filename, file_path = image_gen.create_image(
            screen_request.content,
            screen_request.filename,
            screen_request.width,
            screen_request.height
        )
    
    image_url = f"{base_url}/static/images/{filename}.png"
    
    return ScreenResponse(
        status="success",
        image_url=image_url,
        filename=filename
    )

@app.get("/api/current_screen", response_model=DisplayResponse)
async def current_screen(
    request: Request,
    id: str = Header(..., description="Device MAC address"),
    access_token: str = Header(None, alias="Access-Token")
):
    """Get current screen without advancing playlists (open access)."""
    
    # For now, return the same as display endpoint but without updating last_seen
    base_url = get_base_url(request)
    
    # Try to get device info if it exists
    device = db.get_device(id)
    device_name = device.friendly_id if device else id
    last_seen = device.last_seen.strftime('%Y-%m-%d %H:%M:%S UTC') if device and device.last_seen else 'Never'
    battery = device.battery_voltage if device else 'Unknown'
    firmware = device.firmware_version if device else 'Unknown'
    
    content = f"""Current Screen

Device: {device_name}
MAC: {id}
Last Seen: {last_seen}
Battery: {battery}V
Firmware: {firmware}

Server Status: Running
Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"""

    filename, file_path = image_gen.create_image(content=content)
    image_url = f"{base_url}/static/images/{filename}.png"
    
    return DisplayResponse(
        status=0,
        image_url=image_url,
        filename=filename,
        refresh_rate=60,  # Refresh every 1 minute for faster updates
        update_firmware=False,
        firmware_url=None,
        reset_firmware=False,
        special_function="sleep",
        image_url_timeout=30
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            status=2,
            error="Internal Server Error",
            message=str(exc),
            retry_after=300
        ).dict()
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)