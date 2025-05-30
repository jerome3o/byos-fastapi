import os
import secrets
import string
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Header, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .database import Database
from .image_utils import ImageGenerator
from .models import (
    Device,
    DeviceLog,
    DisplayResponse,
    ErrorResponse,
    ScreenRequest,
    ScreenResponse,
    SetupResponse,
)

REFRESH_RATE = 900  # Default refresh rate in seconds (15 minutes)
latest_image_filename = None  # Store the single latest image filename

app = FastAPI(
    title="TRMNL Custom Server",
    description="Custom FastAPI server for TRMNL e-ink devices",
    version="1.0.0",
)

# Initialize components
db = Database()
image_gen = ImageGenerator()

# Mount static files for serving images
os.makedirs("static/images", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


def generate_api_key() -> str:
    """Generate a secure API key."""
    return "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(32)
    )


def generate_friendly_id() -> str:
    """Generate a short friendly device ID."""
    return "".join(
        secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6)
    )


def get_base_url(request: Request) -> str:
    """Get the base URL for image serving."""
    return f"{request.url.scheme}://{request.headers.get('host', 'localhost')}"


# Authentication removed - all endpoints now have open access


@app.get("/")
async def root():
    """Root endpoint - serves the web frontend."""
    return FileResponse("static/frontend/index.html")


@app.get("/status")
async def status():
    """Server status endpoint."""
    return {
        "message": "TRMNL Custom Server",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/api/display", response_model=DisplayResponse)
async def display_endpoint(
    request: Request,
    id: str = Header(..., description="Device MAC address"),
    access_token: str = Header(None, alias="Access-Token"),
    refresh_rate: int | None = Header(None, alias="Refresh-Rate"),
    battery_voltage: float | None = Header(None, alias="Battery-Voltage"),
    fw_version: str | None = Header(None, alias="FW-Version"),
    rssi: int | None = Header(None, alias="RSSI"),
    width: int | None = Header(800, alias="Width"),
    height: int | None = Header(480, alias="Height"),
):
    """Primary device endpoint for screen content delivery (open access)."""

    # Update device status
    db.update_device_status(
        id,
        last_seen=datetime.utcnow(),
        firmware_version=fw_version,
        battery_voltage=battery_voltage,
    )

    # Generate or get current image
    base_url = get_base_url(request)

    # Check if we have any latest image, otherwise use HELLO WORLD
    global latest_image_filename
    if latest_image_filename:
        filename = latest_image_filename
        image_url = f"{base_url}/static/images/{filename}.png"
    else:
        # Create big HELLO WORLD image as default
        filename, file_path = image_gen.create_hello_world_image()
        image_url = f"{base_url}/static/images/{filename}.png"

    return DisplayResponse(
        status=0,
        image_url=image_url,
        filename=filename,
        refresh_rate=REFRESH_RATE,
        update_firmware=False,
        firmware_url=None,
        reset_firmware=False,
        special_function="sleep",
        image_url_timeout=30,
    )


@app.post("/api/setup", response_model=SetupResponse)
async def setup_endpoint(
    request: Request,
    id: str = Header(..., description="Device MAC address"),
    fw_version: str | None = Header(None, alias="FW-Version"),
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
            message="Welcome back to your TRMNL server",
        )

    # Create new device
    api_key = generate_api_key()
    friendly_id = generate_friendly_id()

    new_device = Device(
        mac_address=id,
        api_key=api_key,
        friendly_id=friendly_id,
        created_at=datetime.utcnow(),
        firmware_version=fw_version,
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
        message="Welcome to your custom TRMNL server",
    )


@app.post("/api/log")
async def log_endpoint(
    log_data: DeviceLog,
    id: str = Header(..., description="Device MAC address"),
    access_token: str = Header(None, alias="Access-Token"),
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
            battery_voltage=log_data.battery_voltage,
        )

    return {"status": "success", "message": "Log data received"}


@app.post("/api/screens", response_model=ScreenResponse)
async def create_screen(
    screen_request: ScreenRequest,
    request: Request,
    id: str = Header(None, description="Device MAC address"),
    access_token: str = Header(None, alias="Access-Token"),
):
    """Create new screen content programmatically (open access)."""

    base_url = get_base_url(request)

    if screen_request.content_type == "html":
        filename, file_path = image_gen.html_to_image(
            screen_request.content, screen_request.filename
        )
    elif screen_request.content_type == "big_text":
        # Use big text generation for maximum screen coverage
        filename, file_path = image_gen.create_big_text_image(
            screen_request.content, 
            filename=screen_request.filename,
            width=screen_request.width,
            height=screen_request.height,
        )
    elif screen_request.content_type == "uri":
        # Handle data URI (base64 encoded images from canvas)
        filename, file_path = image_gen.data_uri_to_image(
            screen_request.content, screen_request.filename
        )
    else:
        # For other content types, treat as text for now
        filename, file_path = image_gen.create_image(
            screen_request.content,
            screen_request.filename,
            screen_request.width,
            screen_request.height,
        )

    image_url = f"{base_url}/static/images/{filename}.png"

    # Store as the latest image (single device mode)
    global latest_image_filename
    latest_image_filename = filename

    return ScreenResponse(status="success", image_url=image_url, filename=filename)


@app.post("/api/refresh_rate")
async def set_refresh_rate(
    request: Request,
    refresh_rate: int = Header(..., alias="Refresh-Rate"),
):
    """Set refresh rate globally (single device mode)."""
    if refresh_rate < 60 or refresh_rate > 3600:
        return JSONResponse(
            status_code=400,
            content={"error": "Refresh rate must be between 60 and 3600 seconds"}
        )
    
    global REFRESH_RATE
    REFRESH_RATE = refresh_rate
    return {"status": "success", "message": f"Refresh rate set to {refresh_rate}s globally"}


@app.get("/api/current_screen", response_model=DisplayResponse)
async def current_screen(
    request: Request,
    id: str = Header(..., description="Device MAC address"),
    access_token: str = Header(None, alias="Access-Token"),
):
    """Get current screen without advancing playlists (open access)."""

    # For now, return the same as display endpoint but without updating last_seen
    base_url = get_base_url(request)

    # Try to get device info if it exists
    device = db.get_device(id)
    device_name = device.friendly_id if device else id
    last_seen = (
        device.last_seen.strftime("%Y-%m-%d %H:%M:%S UTC")
        if device and device.last_seen
        else "Never"
    )
    battery = device.battery_voltage if device else "Unknown"
    firmware = device.firmware_version if device else "Unknown"

    content = f"""Current Screen

Device: {device_name}
MAC: {id}
Last Seen: {last_seen}
Battery: {battery}V
Firmware: {firmware}

Server Status: Running
Time: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}"""

    filename, file_path = image_gen.create_image(content=content)
    image_url = f"{base_url}/static/images/{filename}.png"

    return DisplayResponse(
        status=0,
        image_url=image_url,
        filename=filename,
        refresh_rate=REFRESH_RATE,
        update_firmware=False,
        firmware_url=None,
        reset_firmware=False,
        special_function="sleep",
        image_url_timeout=30,
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            status=2, error="Internal Server Error", message=str(exc), retry_after=300
        ).dict(),
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
